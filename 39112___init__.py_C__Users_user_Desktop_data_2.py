# PyMoBu - Python enhancement for Autodesk's MotionBuilder
# Copyright (C) 2010  Scott Englert
# scott@scottenglert.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
Component module

Contains component classes and related functions
'''
import re

from pyfbsdk import FBComponent #@UnresolvedImport
from pyfbsdk import FBPropertyType #@UnresolvedImport
from pyfbsdk import FBMatrix #@UnresolvedImport
from pyfbsdk import FBVector3d #@UnresolvedImport
from pyfbsdk import FBModelTransformationType #@UnresolvedImport
from pyfbsdk import FBNamespaceAction #@UnresolvedImport

# eclipseSyntax
if False: from pyfbsdk_gen_doc import * #@UndefinedVariable @UnusedWildImport

def ConvertToPyMoBu(component):
    '''Utility to convert a FB class to a PMB class'''
    if isinstance(component, PMBComponent):
        return component
    
    # get the first two inherited classes
    componentClasses = component.__class__.__mro__
    
    for fbClass in componentClasses:
        pmbClassName = fbClass.__name__.replace('FB', 'PMB')
    
        try:
            pmbClass = eval(pmbClassName)
        except:
            continue
        
        return pmbClass.Convert(component)
    
# add this function to FBComponent
FBComponent.ConvertToPyMoBu = ConvertToPyMoBu    

# -----------------------------------------------------
# PyMoBu Component Classes
# -----------------------------------------------------
class PMBComponent(object):
    '''PyMoBu class for FBComponent'''
    
    # property type dictionary {Name : [enum, internal name]}
    kPropertyTypes = dict(Action = [FBPropertyType.kFBPT_Action, 'Action'],
                          Enum = [FBPropertyType.kFBPT_enum, 'Enum'],
                          Integer = [FBPropertyType.kFBPT_int,'Integer'],
                          Bool = [FBPropertyType.kFBPT_bool,'Bool'],
                          Double = [FBPropertyType.kFBPT_double,'Number'],
                          CharPtr = [FBPropertyType.kFBPT_charptr, 'String'],
                          Float = [FBPropertyType.kFBPT_float,'Float'],
                          Time = [FBPropertyType.kFBPT_Time, 'Time'],
                          Object = [FBPropertyType.kFBPT_object, 'Object'],
                          StringList = [FBPropertyType.kFBPT_stringlist, 'StringList'],
                          Vector4D = [FBPropertyType.kFBPT_Vector4D, 'Vector'],
                          Vector3D = [FBPropertyType.kFBPT_Vector3D, 'Vector'],
                          Vector2D = [FBPropertyType.kFBPT_Vector2D, 'Vector'],
                          ColorRGB = [FBPropertyType.kFBPT_ColorRGB, 'Color'],
                          ColorRGBA = [FBPropertyType.kFBPT_ColorRGBA, 'ColorAndAlpha'],
                          TimeSpan = [FBPropertyType.kFBPT_TimeSpan, 'Time'])
    
    def __init__(self, component):
        self.component = component

    def __repr__(self):
        name  = getattr(self.component, 'LongName', self.component.Name)
        return "%s('%s')" % (self.__class__.__name__, name)
    
    def __str__(self):
        '''Returns the full object name'''
        return getattr(self.component, 'LongName', self.component.Name)
    
    @property
    def Name(self):
        '''Returns the object name'''
        return getattr(self.component, 'Name', self.component.Name)
    
    @property
    def LongName(self):
        '''Returns the full object name'''
        return getattr(self.component, 'LongName', self.component.Name)
       
    @classmethod
    def Convert(cls, component):
        return cls(component)
                
    def ListProperties(self, pattern=None, _type=None, **kwargs):
        '''
        Returns a list of property names from the PropertyList with optional filters
        @param pattern: list properties with specific names with optional wildcard *. Default is all.
        @param _type: get properties of specific types. See self.kPropertyTypes.keys() for names
        
        Optional parameters True/False for testing from FBProperty:
        IsAnimatable
        IsInternal
        IsList
        IsMaxClamp
        IsMinClamp
        IsObjectList
        IsReadOnly
        IsReferenceProperty
        IsUserProperty
        '''
        # setup a test for the optional parameters
        def passesOptionalTest(x):
            for arg, challenge in kwargs.iteritems():
                func = getattr(x, arg, None)
                if func and func() != challenge:
                    return False
            return True
            
        # set up the name testing based on the pattern
        if pattern:           
            # if there is a wild card in the pattern
            if '*' in pattern:
                pattern = pattern.replace('*', '.*')
                # name testing function
                passesNameTest = lambda x: re.match(pattern, x.GetName())
            else:
                passesNameTest = lambda x: pattern == x.GetName()      
        else:
            passesNameTest = lambda x: True
        
        # add type testing
        if _type:
            propertyType = self.kPropertyTypes[_type][0]
            passesTypeTest = lambda x: x.GetPropertyType() == propertyType
        else:
            passesTypeTest = lambda x: True
            
        properties = []
        for p in self.component.PropertyList:
            # odd bug that some items are None
            if p is None:
                continue
            
            if not passesOptionalTest(p):
                continue
            
            if not passesTypeTest(p):
                continue
            
            if passesNameTest(p):
                properties.append(p)
        
        return properties
    
    def GetPropertyValue(self, name):
        '''Returns a property value from the components PropertyList'''
        return self._findProperty(name).Data
        
    def SetPropertyValue(self, name, value):
        '''Sets a property value in the components PropertyList'''
        self._findProperty(name).Data = value
        
    def AddProperty(self, name, _type, animatable=True, user=True):
        '''
        Add a property to this component
        @param name: the name of the property
        @param _type: the data type of the property:   
        '''
        
        if self.ListProperties(pattern=name):
            raise Exception("Can not add property '%s'. Already exists on object '%'" % (name, self))
        try:
            typeData = self.kPropertyTypes[_type]
        except KeyError:
            raise Exception("Invalid property type '%s'. Valid types are: '%s'" % (_type, ', '.join(self.kPropertyTypes.keys())))
        
        typeData.extend([animatable, user, None])
        
        self.component.PropertyCreate(name, *typeData)
    
    def RemoveProperty(self, name):
        '''Remove a property from an object'''
        _property = self._findProperty(name)
# test is we can remove a non-user property or not
        if _property.IsUserProperty():
            self.component.PropertyRemove(_property)
        else:
            raise Exception("Property is flagged as non-user. Unable to remove property '%s' from object '%s'" % (name, self))
    
    def _findProperty(self, name):
        # similar to the native way but raises and exception if property isn't found
        _property = self.component.PropertyList.Find(name)
        if _property:
            return _property
        else:
            raise Exception("Could not find property named '%s' for object '%s'" % (name, self))
    
    def GetNamespace(self):
        '''Returns the namespace of the object'''
        namespace = re.match(".*:", getattr(self.component, 'LongName', self.component.Name))
        if namespace:
            return namespace.group()
    
    def AddNamespace(self, namespace, hierarchy=True, toRight=False):
        '''
        Adds a namespace to the object
        @param hierarchy: Apply this action to hierarchy. Default True
        @param toRight: Add namespace to the right of other namespaces. Default False (left)
        '''
        from pyfbsdk import FBConstraint #@UnresolvedImport @Reimport
        action = FBNamespaceAction.kFBConcatNamespace
        if hierarchy and not isinstance(self.component, FBConstraint):
            self.component.ProcessNamespaceHierarchy(action, namespace, None, toRight)
        else:
            self.component.ProcessObjectNamespace(action, namespace, None, toRight)
            
    def SwapNamespace(self, newNamespace, oldNamespace, hierarchy=True):
        '''
        Swaps a new namespace with an existing namespace
        @param hierarchy: Apply this action to hierarchy. Default True
        '''
        from pyfbsdk import FBConstraint #@Reimport @UnresolvedImport
        action = FBNamespaceAction.kFBReplaceNamespace
        if hierarchy and not isinstance(self.component, FBConstraint):
            self.component.ProcessNamespaceHierarchy(action, newNamespace, oldNamespace)
        else:
            self.component.ProcessObjectNamespace(action, newNamespace, oldNamespace)
    
    def StripNamespace(self, hierarchy=True):
        '''
        Removes all the namespaces
        @param hierarchy: Apply this action to hierarchy. Default True 
        '''
        from pyfbsdk import FBConstraint #@Reimport @UnresolvedImport
        action = FBNamespaceAction.kFBRemoveAllNamespace
        if hierarchy and not isinstance(self.component, FBConstraint):
            self.component.ProcessNamespaceHierarchy(action, '')
        else:
            self.component.ProcessObjectNamespace(action, '')

class PMBBox(PMBComponent):
    '''PyMobu class for FBBox'''
    pass
           
class PMBModel(PMBBox):
    '''PyMoBu class for FBModel'''
    kInverseMatrixTypeDict = dict(Transformation = FBModelTransformationType.kModelInverse_Transformation,
                                  Translation = FBModelTransformationType.kModelInverse_Translation,
                                  Rotation = FBModelTransformationType.kModelInverse_Rotation,
                                  Scaling = FBModelTransformationType.kModelInverse_Scaling)
#                                  Center = FBModelTransformationType.kModelCenter,
#                                  All = FBModelTransformationType.kModelAll)

    kMatrixTypeDict = dict(Transformation = FBModelTransformationType.kModelTransformation,
                           Translation = FBModelTransformationType.kModelTranslation,
                           Rotation = FBModelTransformationType.kModelRotation,
                           Scaling = FBModelTransformationType.kModelScaling)
#                           ParentOffset = FBModelTransformationType.kModelParentOffset)
#                           Center = FBModelTransformationType.kModelCenter,
#                           All = FBModelTransformationType.kModelAll)
    @property
    def Children(self):
        return self.component.Children
       
    @property
    def Parent(self):
        return self.component.Parent
           
    def SetInverseMatrix(self, matrix, worldSpace=False, _type='Transformation'):
        '''
        Set the inverse matrix
        @param worldSpace: world space matrix (True/False) Default False
        @param _type: matrix type (Transformation, Translation, Rotation, Scaling, Center, All)
        '''
        try:
            self.component.SetMatrix(matrix, self.kInverseMatrixTypeDict[_type], worldSpace)
        except KeyError:
            raise Exception("Invalid vector type '%s'. Valid types are: %s" % (_type, ', '.join(self.kInverseMatrixTypeDict.keys())))
        
    def SetMatrix(self, matrix, worldSpace=False, _type='Transformation'):
        '''
        Set the matrix
        @param worldSpace: world space matrix (True/False) Default False
        @param _type: matrix type (Transformation, Translation, Rotation, Scaling, Center, All)
        '''
        try:
            self.component.SetMatrix(matrix, self.kMatrixTypeDict[_type], worldSpace)
        except KeyError:
            raise Exception("Invalid vector type '%s'. Valid types are: %s" % (_type, ', '.join(self.kMatrixTypeDict.keys())))
    
    def GetAnimationNode(self, transform='Translation'):
        '''
        Get AnimationNode
        @param transform: transformation type
        '''
        animationNode= None
        if transform=='Translation':
            animationNode = self.component.Translation.GetAnimationNode()
        if transform=='Rotation':
            animationNode = self.component.Rotation.GetAnimationNode()
        if transform=='Scaling':
            animationNode = self.component.Scaling.GetAnimationNode()
        return animationNode
       
    def GetInverseMatrix(self, worldSpace=False, _type='Transformation'):
        '''
        Get the inverse matrix
        @param worldSpace: world space matrix (True/False) Default False
        @param _type: matrix type (Transformation, Translation, Rotation, Scaling, Center, All)
        ''' 
        matrix = FBMatrix()
        try:
            self.component.GetMatrix(matrix, self.kInverseMatrixTypeDict[_type], worldSpace)
        except KeyError:
            raise Exception("Invalid vector type '%s'. Valid types are: %s" % (_type, ', '.join(self.kInverseMatrixTypeDict.keys())))
        return matrix
        
    def GetMatrix(self, worldSpace=False, _type='Transformation'):
        '''
        Get the matrix
        @param worldSpace: world space matrix (True/False) Default False
        @param _type: matrix type (Transformation, Translation, Rotation, Scaling, Center, All)
        ''' 
        matrix = FBMatrix()
        try:
            self.component.GetMatrix(matrix, self.kMatrixTypeDict[_type], worldSpace)
        except KeyError:
            raise Exception("Invalid vector type '%s'. Valid types are: %s" % (_type, ', '.join(self.kMatrixTypeDict.keys())))
        return matrix
    
    def GetTranslation(self, worldSpace=False):
        '''
        Get translation vector
        @param worldSpace: world space vector (True/False) Default False
        '''
        vector = FBVector3d()
        self.component.GetVector(vector, self.kMatrixTypeDict['Translation'], worldSpace)
        return vector
    
    def GetRotation(self, worldSpace=False):
        '''
        Get rotation vector
        @param worldSpace: world space vector (True/False) Default False
        '''
        vector = FBVector3d()
        self.component.GetVector(vector, self.kMatrixTypeDict['Rotation'], worldSpace)
        return vector
    
    def GetScale(self, worldSpace=False):
        '''
        Get scale vector
        @param worldSpace: world space vector (True/False) Default False
        '''
        vector = FBVector3d()
        self.component.GetVector(vector, self.kMatrixTypeDict['Scaling'], worldSpace)
        return vector
    
    def SetTranslation(self, vector, worldSpace=False):
        '''
        Set the translation vector
        @param worldSpace: world space vector (True/False) Default False
        '''
        self.component.SetVector(vector, self.kMatrixTypeDict['Translation'], worldSpace)
        
    def SetRotation(self, vector, worldSpace=False):
        '''
        Set the rotation vector
        @param worldSpace: world space vector (True/False) Default False
        '''
        self.component.SetVector(vector, self.kMatrixTypeDict['Rotation'], worldSpace)
        
    def SetScale(self, vector, worldSpace=False):
        '''
        Set the scale vector
        @param worldSpace: world space vector (True/False) Default False
        '''
        self.component.SetVector(vector, self.kMatrixTypeDict['Scaling'], worldSpace)
            
# import other component modules
from pymobu.components.constraints import *
