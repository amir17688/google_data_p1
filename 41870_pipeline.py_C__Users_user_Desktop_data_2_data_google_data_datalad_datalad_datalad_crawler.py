# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Pipeline functionality.

Pipeline is represented by a simple list or tuple of nodes or other nested pipelines.
Each pipeline node is a callable which receives a dictionary (commonly named `data`),
does some processing and yields (once or multiple times) a derived dictionary (commonly
a shallow copy of original dict).  For a node to be parametrized it should be
implemented as a callable (i.e. define __call__) class, which could obtain parameters
in its constructor.

TODO:  describe   PIPELINE_OPTS  and how to specify them for a give (sub-)pipeline.

`data` dictionary is used primarily to carry the scraped/produced data, but besides that
it will carry few items which some nodes might use.  All those item names will start with
`datalad_` prefix, and will be intended for 'inplace' modifications or querying.
Following items are planned to be provided by the pipeline runner:

`datalad_settings`
   PipelineSettings object which would could be used to provide configuration for current
   run of the pipeline. E.g.

   - dry:  either nodes are intended not to perform any changes which would reflect on disk
   - skip_existing:

`datalad_stats`
   ActivityStats/dict object to accumulate statistics on what has been done by the nodes
   so far

To some degree, we could make an analogy of a `blood` to `data` and `venous system` to
`pipeline`.  Blood delivers various elements, which are picked up by various parts of
our body, whenever they know what to do with corresponding elements.  To the same degree
nodes can consume, augment, or produce new items to the `data` and send it down the stream.
Since there is no strict typing or specification on what nodes could consume or produce (yet)
no verification is done and things can go utterly wrong.  So nodes must be robust and
provide informative logging.
"""

import sys
from glob import glob
from six import iteritems
from os.path import dirname, join as opj, isabs, exists, curdir, basename

from .. import cfg
from ..consts import CRAWLER_META_DIR, HANDLE_META_DIR, CRAWLER_META_CONFIG_PATH
from ..utils import updated
from ..dochelpers import exc_str
from ..support.gitrepo import GitRepo
from ..support.stats import ActivityStats
from ..support.configparserinc import SafeConfigParserWithIncludes

# Name of the section in the config file which would define pipeline parameters
CRAWLER_PIPELINE_SECTION = 'crawler'

from logging import getLogger
lgr = getLogger('datalad.crawl.pipeline')


class FinishPipeline(Exception):
    """Exception to use to signal that any given pipeline should be stopped
    """
    pass

# Options which could augment behavior of the pipeline, could be specified
# only on top of it
PIPELINE_OPTS = dict(
    # nested_pipeline_inherits_opts=True,
    # would use or not values yielded by the nested pipeline
    output='input',    # last-output, outputs, input+outputs
    loop=False,        # either to feed results into itself (until None returned)
)

# which data types depict object being a pipeline
PIPELINE_TYPES = (list, tuple)

def reset_pipeline(pipeline):
    """Given a pipeline, traverses its nodes and calls .reset on them if they have such an attribute
    """
    if pipeline:
        for node in pipeline:
            if isinstance(node, PIPELINE_TYPES):
                reset_pipeline(node)
            elif hasattr(node, '__call__') and hasattr(node, 'reset'):
                lgr.log(2, "Resetting node %s" % node)
                node.reset()

def run_pipeline(*args, **kwargs):
    """Run pipeline and assemble results into a list

    Byt default pipeline returns only its input (see PIPELINE_OPTS),
    so if no options for the pipeline were given to return additional
    items, a `[{}]` will be provided as output
    """
    output = list(xrun_pipeline(*args, **kwargs))
    stats = None
    if output:
        if 'datalad_stats' in output[-1]:
            stats = output[-1]['datalad_stats'].get_total()
            stats_str = stats.as_str(mode='line')
        else:
            stats_str = 'no stats collected'
    else:
        stats_str = "no output"
    lgr.info("Finished running pipeline: %s" % stats_str)
    return output if output else None


def _get_pipeline_opts(pipeline):
    """Return options and pipeline steps to be ran given the pipeline "definition"

    Definition might have options as the first element
    """
    opts = PIPELINE_OPTS.copy()
    if isinstance(pipeline[0], dict):
        newopts, pipeline = (pipeline[0], pipeline[1:])
        opts = updated(opts, newopts)
    return opts, pipeline


def xrun_pipeline(pipeline, data=None, stats=None, reset=True):
    """Yield results from the pipeline.

    """
    id_pipeline = "Pipe #%s" % id(pipeline)

    def _log(msg, *args):
        """Helper for uniform debug messages"""
        lgr.log(5, "%s: " + msg, id_pipeline, *args)

    _log("%s", pipeline)

    if reset:
        _log("Resetting pipeline")
        reset_pipeline(pipeline)

    # just for paranoids and PEP8-disturbed, since theoretically every node
    # should not change the data, so having default {} should be sufficient
    data = data or {}

    if 'datalad_stats' in data:
        if stats is not None:
            raise ValueError("We were provided stats to use, but data has already datalad_stats")
    else:
        data = updated(data, {'datalad_stats': stats or ActivityStats()})

    if not len(pipeline):
        return

    # options for this pipeline
    opts, pipeline = _get_pipeline_opts(pipeline)

    # verify that we know about all specified options
    unknown_opts = set(opts).difference(set(PIPELINE_OPTS))
    if unknown_opts:
        raise ValueError("Unknown pipeline options %s" % str(unknown_opts))

    data_to_process = [data]
    output = opts['output']
    if output not in ('input',  'last-output', 'outputs', 'input+outputs'):
        raise ValueError("Unknown output=%r" % output)

    if opts['loop'] and output == 'input':
        lgr.debug("Assigning output='last-output' for sub-pipeline since we want to loop until pipeline returns anything")
        output_sub = 'last-output'
    else:
        output_sub = output

    log_level = lgr.getEffectiveLevel()
    data_out = None
    while data_to_process:
        _log("processing data. %d left to go", len(data_to_process))
        data_in = data_to_process.pop(0)
        try:
            for idata_out, data_out in enumerate(xrun_pipeline_steps(pipeline, data_in, output=output_sub)):
                if log_level <= 3:
                        # provide details of what keys got changed
                        # TODO: unify with 2nd place where it was invoked
                        lgr.log(3, "O3: +%s, -%s, ch%s, ch?%s", *_compare_dicts(data_in, data_out))

                _log("got new %dth output", idata_out)
                if opts['loop']:
                    _log("extending list of data to process due to loop option")
                    data_to_process.append(data_out)
                if 'outputs' in output:
                    _log("yielding output")
                    yield data_out
        except FinishPipeline as e:
            # TODO: decide what we would like to do -- skip that particular pipeline run
            # or all subsequent or may be go back and only skip that generated result
            _log("got a signal that pipeline is 'finished'")

    # TODO: this implementation is somewhat bad since all the output logic is
    # duplicated within xrun_pipeline_steps, but it is probably unavoidable because of
    # loop option
    if output == 'last-output':
        if data_out:
            _log("yielding last-output")
            yield data_out

    # Input should be yielded last since otherwise it might ruin the flow for typical
    # pipelines which do not expect anything beyond going step by step
    # We should yeild input data even if it was empty
    if ('input' in output):
        _log("finally yielding input data as instructed")
        yield data


def xrun_pipeline_steps(pipeline, data, output='input'):
    """Actually run pipeline steps, feeding yielded results to the next node
    and yielding results back

    Recursive beast which runs a single node and then recurses to run the rest,
    possibly multiple times if current node is a generator.
    It yields output from the node/nested pipelines, as directed by output
    argument.
    """
    if not len(pipeline):
        return

    node, pipeline_tail = pipeline[0], pipeline[1:]

    if isinstance(node, (list, tuple)):
        lgr.debug("Pipe: %s" % str(node))
        # we have got a step which is yet another entire pipeline
        pipeline_gen = xrun_pipeline(node, data, reset=False)
        if pipeline_gen:
            # should be similar to as running a node
            data_in_to_loop = pipeline_gen
        else:
            # pipeline can return None, and in such a case
            # just do not process further, since if it completed
            # normally, its input would have been provided back
            lgr.log(7, "Pipeline generator %s returned None", node)
            data_in_to_loop = []
        prev_stats = None  # we do not care to check if entire pipeline drops stats
                           # since it is done below at the node level
    else:  # it is a "node" which should generate (or return) us an iterable to feed
           # its elements into the rest of the pipeline
        lgr.debug("Node: %s" % node)
        prev_stats = data.get('datalad_stats', None)  # so we could check if node doesn't dump it
        data_in_to_loop = node(data)

    log_level = lgr.getEffectiveLevel()
    data_out = None
    if data_in_to_loop:
        for data_ in data_in_to_loop:
            if prev_stats is not None:
                new_stats = data_.get('datalad_stats', None)
                if new_stats is None or new_stats is not prev_stats:
                    lgr.debug("Node %s has changed stats to %s from %s. Updating and using previous one",
                              node, prev_stats, new_stats)
                    if new_stats is not None:
                        prev_stats += new_stats
                    data_['datalad_stats'] = prev_stats
            if log_level <= 4:
                # provide details of what keys got changed
                stats_str = data_['datalad_stats'].as_str(mode='line') if 'datalad_stats' in data_ else ''
                lgr.log(4, "O1: +%s, -%s, ch%s, ch?%s %s", *(_compare_dicts(data, data_) + (stats_str,)))
            if pipeline_tail:
                lgr.log(7, " pass %d keys into tail with %d elements", len(data_), len(pipeline_tail))
                lgr.log(5, " passed keys: %s", data_.keys())
                for data_out in xrun_pipeline_steps(pipeline_tail, data_, output=output):
                    if log_level <= 3:
                        # provide details of what keys got changed
                        # TODO: difference from previous stats!
                        stats_str = data_['datalad_stats'].as_str(mode='line') if 'datalad_stats' in data_ else ''
                        lgr.log(3, "O2: +%s, -%s, ch%s, ch?%s %s", *(_compare_dicts(data, data_out) + (stats_str,)))
                    if 'outputs' in output:
                        yield data_out
            else:
                data_out = data_
                if 'outputs' in output:
                    yield data_out
    elif pipeline_tail:
        lgr.warning("%s returned None, although there is still a tail in the pipeline" % node)

    if output == 'last-output' and data_out:
        yield data_out


def _compare_dicts(d1, d2):
    """Given two dictionary, return what keys were added, removed, changed or may be changed
    """
    added, removed, changed, maybe_changed = [], [], [], []
    all_keys = set(d1).union(set(d2))
    for k in all_keys:
        if k not in d1:
            added.append(k)
        elif k not in d2:
            removed.append(k)
        else:
            if (d1[k] is d2[k]):
                continue
            else:
                try:
                    if d1[k] != d2[k]:
                        changed.append(k)
                except:
                    maybe_changed.append(k)
    return added, changed, removed, maybe_changed


def load_pipeline_from_script(filename, **opts):
    # mod = __import__('datalad.crawler.pipelines.%s' % filename, fromlist=['datalad.crawler.pipelines'])
    dirname_ = dirname(filename)
    assert(filename.endswith('.py'))
    try:
        sys.path.insert(0, dirname_)
        modname = basename(filename)[:-3]
        # To allow for relative imports within "stock" pipelines
        if dirname_ == opj(dirname(__file__), 'pipelines'):
            mod = __import__('datalad.crawler.pipelines.%s' % modname,
                             fromlist=['datalad.crawler.pipelines'])
        else:
            mod = __import__(modname, level=0)
        return mod.pipeline(**opts)
    except Exception as e:
        raise RuntimeError("Failed to import pipeline from %s: %s" % (filename, exc_str(e)))
    finally:
        if dirname_ in sys.path:
            path = sys.path.pop(0)
            if path != dirname_:
                lgr.warning("Popped %s when expected %s. Restoring!!!" % (path, dirname_))
                sys.path.insert(0, path)


def _find_pipeline(name):
    """Given a name for a pipeline, looks for it under common locations
    """
    def candidates(name):
        if not name.endswith('.py'):
            name = name + '.py'

        # first -- current directory
        repo_path = GitRepo.get_toppath(curdir)
        if repo_path:
            yield opj(repo_path, CRAWLER_META_DIR, 'pipelines', name)

        # TODO: look under other .datalad locations as well

        # last -- within datalad code
        yield opj(dirname(__file__), 'pipelines', name)  # datalad's module shipped within it

    for candidate in candidates(name):
        if exists(candidate):
            lgr.debug("Found pipeline %s under %s", name, candidate)
            return candidate
        lgr.log(5, "No pipeline %s under %s", name, candidate)

    return None


def load_pipeline_from_template(name, opts={}):
    """Given a name, loads that pipeline from datalad.crawler.pipelines

    and later from other locations

    Parameters
    ----------
    name: str
        Name of the pipeline defining the filename. Or full path to it (TODO)
    opts: dict, optional
        Options for the pipeline, passed as **kwargs into the pipeline call
    """

    if (isabs(name) or exists(name)):
        raise NotImplementedError("Don't know how to import straight path %s yet" % name)

    # explicit isabs since might not exist
    filename = name \
        if (isabs(name) or exists(name)) \
        else _find_pipeline(name)

    if filename:
        if not exists(filename):
            raise IOError("Pipeline file %s is N/A" % filename)
    else:
        raise ValueError("could not find pipeline for %s" % name)

    return load_pipeline_from_script(filename, **opts)

# TODO: we might need to find present .datalad/crawl in another branch if not
# present currently

def load_pipeline_from_config(path):
    """Given a path to the pipeline configuration file, instantiate a pipeline
    """

    cfg = SafeConfigParserWithIncludes()
    cfg.read([path])
    if cfg.has_section(CRAWLER_PIPELINE_SECTION):
        opts = cfg.options(CRAWLER_PIPELINE_SECTION)
        # must have template
        if 'template' not in opts:
            raise IOError("%s lacks %r field within %s section"
                          % (path, 'template', CRAWLER_PIPELINE_SECTION))
        opts.pop(opts.index('template'))
        template = cfg.get(CRAWLER_PIPELINE_SECTION, 'template')
        pipeline = load_pipeline_from_template(
            template,
            {o: cfg.get(CRAWLER_PIPELINE_SECTION, o) for o in opts})
    else:
        raise IOError("Did not find section %r within %s" % (CRAWLER_PIPELINE_SECTION, path))
    return pipeline


def get_repo_pipeline_config_path(repo_path=curdir):
    """Given a path within a repo, return path to the crawl.cfg"""
    if not exists(opj(repo_path, HANDLE_META_DIR)):
        # we need to figure out top path for the repo
        repo_path = GitRepo.get_toppath(repo_path)
        if not repo_path:
            return None
    return opj(repo_path, CRAWLER_META_CONFIG_PATH)


def get_repo_pipeline_script_path(repo_path=curdir):
    """If there is a single pipeline present among pipelines/ return path to it"""
    # TODO: somewhat adhoc etc -- may be improve with some dedicated name being
    # tracked or smth like that
    if not exists(opj(repo_path, HANDLE_META_DIR)):
        # we need to figure out top path for the repo
        repo_path = GitRepo.get_toppath(repo_path)
        if not repo_path:
            return None
    pipelines = glob(opj(repo_path, CRAWLER_META_DIR, 'pipelines', '*.py'))
    if len(pipelines) > 1 or not pipelines:
        return None
    return pipelines[0]