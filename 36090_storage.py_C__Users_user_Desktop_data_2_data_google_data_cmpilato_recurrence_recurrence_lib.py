# ====================================================================
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ====================================================================

"""storage.py:  Recurrence storage/persistance routines."""


import events
import datetime


LATEST_VERSION = 1


def parse_data_file_v1(fp):
  definitions = {}
  occurrences = []

  def unescape_piece(piece):
    piece = piece.replace('\\r', '\r')
    piece = piece.replace('\\n', '\n')
    piece = piece.replace('\\t', '\t')
    piece = piece.replace('\\\\', '\\')
    return piece

  def parse_date(datestr):
    if datestr == '':
      return None
    date_pieces = map(lambda x: int(x), datestr.split('-'))
    assert len(date_pieces) == 3
    return datetime.date(date_pieces[0], date_pieces[1], date_pieces[2])
  
  while 1:
    line = fp.readline()
    if not line:
      break
    line = line.rstrip('\n\r')
    pieces = map(lambda x: unescape_piece(x), line.split('\t'))
    if pieces[0] == 'EventDefinition':
      er = None
      if len(pieces) > 4:
        er = events.EventRecurrence(events.period_from_string(pieces[4]),
                                    parse_date(pieces[5]))
      ed = events.EventDefinition(pieces[1], pieces[2],
                                  parse_date(pieces[3]), er)
      definitions[ed.get_uuid()] = ed
    elif pieces[0] == 'EventOccurrence':
      eo = events.EventOccurrence(definitions[pieces[1]],
                                  parse_date(pieces[2]),
                                  pieces[3] == 'true' and True or False)
      occurrences.append(eo)
    else:
      raise Exception("Unrecognized record type.")
  return definitions.values(), occurrences

      
def read_data_file(filepath):
  """Parse a Recurrence data file, returning"""
  version = None
  fp = open(filepath, 'r')
  try:
    version_line = fp.readline().rstrip('\n\r')
    if version_line.startswith('#version = '):
      version = int(version_line[11:])
    if version == 1:
      return parse_data_file_v1(fp)
    else:
      raise Exception("Unrecognized data file format for file '%s'."
                      % (filepath))
  except:
    raise
  

def unparse_date_file_v1(filepath, definitions, occurrences):

  def escape_piece(piece):
    piece = str(piece)
    piece = piece.replace('\\', '\\\\')
    piece = piece.replace('\t', '\\t')
    piece = piece.replace('\n', '\\n')
    piece = piece.replace('\r', '\\r')
    return piece

  def unparse_date(date):
    if date is None:
      return ''
    else:
      return "%d-%02d-%02d" % (date.year, date.month, date.day)
  
  def unparse_pieces(pieces):
    return '\t'.join(map(lambda x: escape_piece(x), pieces)) + '\n'

  def definition_to_pieces(definition):
    pieces = ['EventDefinition',
              definition.get_uuid(),
              definition.get_description(),
              unparse_date(definition.get_start_date()),
              ]
    recurrence = definition.get_recurrence()
    if recurrence:
      pieces.extend([events.period_to_string(recurrence.get_period()),
                     unparse_date(recurrence.get_until_date()),
                     ])
    return pieces

  def occurrence_to_pieces(occurrence):
    return ['EventOccurrence',
            occurrence.get_definition().get_uuid(),
            unparse_date(occurrence.get_date()),
            occurrence.get_cleared() and 'true' or 'false',
            ]
    
  fp = open(filepath, 'w')
  fp.write('#version = 1\n')
  for definition in definitions:
    fp.write(unparse_pieces(definition_to_pieces(definition)))
  for occurrence in occurrences:
    fp.write(unparse_pieces(occurrence_to_pieces(occurrence)))
  fp.close()


def write_data_file(filepath, definitions, occurrences, version=LATEST_VERSION):
  assert(version == LATEST_VERSION)
  unparse_date_file_v1(filepath, definitions, occurrences)
