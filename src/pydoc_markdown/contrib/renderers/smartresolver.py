# -*- coding: utf8 -*-
# Copyright (c) 2019 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import typing as t

import docspec
import os
from pydoc_markdown.interfaces import Renderer, Resolver
from pydoc_markdown.util.pages import Page, Pages

class SmartReferenceResolver(Resolver):
    def __init__(self, modules: t.List[docspec.Module], renderer: Renderer = None) -> None:
        
        self.renderer = renderer
        self.modules = modules.copy()
        self.pages : Pages[Page] = renderer.pages
        self.markdown = self.renderer.markdown
        
        super().__init__()

    def GetObjectID(self, obj: docspec.ApiObject) -> str:
        parts = []
        while obj:
            parts.append(obj.name)
            obj = obj.parent
        return '.'.join(reversed(parts))
    
    def GetObjectModule(self, obj: docspec.ApiObject) -> docspec.Module:
        while type(obj) != docspec.Module:
            obj = obj.parent
        return obj


    def FindModuleByName(self, moduleName : str) -> t.Optional[docspec.Module]:
        for module in self.modules:
            if module.name == moduleName:
                return module
        return None

    def FindRefInModule(self,
                        module     : docspec.Module,
                        refNames   : t.List[str],
                        typeFilter : t.List[t.Type[docspec.ApiObject]] = []
        ) -> t.Optional[docspec.ApiObject]:
        
        if isinstance(refNames, str): refNames = [refNames]
        
        def find(module: docspec.Module, name: str) -> t.Optional[docspec.ApiObject]:

            for member in module.members:
                if  member.name == partName \
                    and ((len(typeFilter) == 0) or (type(member) in typeFilter)) \
                    and not isinstance(member, docspec.Indirection):
                    return member

            return None

        checkObj = module
        for partName in refNames:
            if not isinstance(checkObj, docspec.HasMembers): return None
            
            # checkObj = next((member for member in checkObj.members if member.name == partName and not isinstance(member, docspec.Indirection)), None)
            checkObj = find(checkObj, partName)
            if checkObj == None: break
            
        return checkObj

    def FindAllReference(self,
                        obj        : docspec.ApiObject,
                        refNames   : t.List[str],
                        typeFilter : t.List[t.Type[docspec.ApiObject]] = [],
                        excpt      : docspec.ApiObject = None,
                        inherited  : bool = False
        ) -> t.Tuple[t.List[docspec.ApiObject], t.List[docspec.ApiObject]]:
        """
        Find all the references in all files 
        """
        
        easyFind = self.FindRefInModule(obj, refNames[-1], typeFilter)
        hardFind = self.FindRefInModule(obj, refNames, typeFilter)
        easyResults = [easyFind] if easyFind != None else []
        hardResults = [hardFind] if hardFind != None else []
        
        if isinstance(obj, docspec.HasMembers):
            for member in obj.members:
                if member != excpt:
                    search = self.FindAllReference(member, refNames, typeFilter, None, True)
                    easyResults.extend(search[0])
                    hardResults.extend(search[1])
            
        if not inherited:
            
            parent = obj.parent

            if parent == None:
                for module in self.modules:
                    if module != excpt:
                        search = self.FindAllReference(module, refNames, typeFilter, None, True)
                        easyResults.extend(search[0])
                        hardResults.extend(search[1])
            else:
                search = self.FindAllReference(parent, refNames, typeFilter, obj, False)
                easyResults.extend(search[0])
                hardResults.extend(search[1])

        return (easyResults, hardResults)

    def FindRefLocal(self,
                    obj        : docspec.ApiObject,
                    refNames   : t.List[str],
                    typeFilter : t.List[t.Type[docspec.ApiObject]] = []
        ) -> t.Optional[docspec.ApiObject]:
        """
        Find the reference in the current object
        """

        localModule = obj
        backcheck = len(refNames) - (0 if isinstance(obj, docspec.Function) else 1)
        for i in range(backcheck):
            localModule = localModule.parent
            if localModule == None: return None
        
        localScopeRef = self.FindRefInModule(localModule, refNames, typeFilter)
        if localScopeRef: return localScopeRef

        return self.FindRefInModule(self.GetObjectModule(obj), refNames, typeFilter)
    
    def FindRefFromImport(self,
                        module         : docspec.Module,
                        refNames       : t.List[str],
                        typeFilter     : t.List[t.Type[docspec.ApiObject]] = [],
                        previousModule : docspec.Module = None
        ) -> t.Optional[docspec.ApiObject]:

        # if module is not a module, get its parent module  
        if type(module) != docspec.Module:
            module = self.GetObjectModule(module)


        # find the reference in this module
        checkObj = self.FindRefInModule(module, refNames, typeFilter)
        if checkObj: return checkObj
        

        # process imports info
        _imports : t.List[ImportInfo] = []
        _imports_all : t.List[ImportInfo] = []

        for _import in module.members:
            if isinstance(_import, docspec.Indirection):
                info = ImportInfo(self, module, _import)
                iter([_imports_all.append(info) if info.isImportAll else _imports.append(info)])
        

        for _import in _imports:
            if _import.importAsName == refNames[0]:
                if _import.Process():

                    if _import.module == previousModule:
                        # recursive, won't be any good
                        return None

                    newRefNames = refNames
                    if _import.isImportModule:
                        newRefNames = refNames[1:]
                    else:
                        newRefNames[0] = _import.importedObjects[0]
                    
                    result = self.FindRefFromImport(_import.module, newRefNames, typeFilter, module)
                    if result: return result
                else:
                    return None
        


        for _import in _imports_all:

            if _import.Process():

                if _import.module == previousModule:
                    # recursive, won't be any good
                    return None

                result = self.FindRefFromImport(_import.module, refNames, typeFilter, module)
                if result: return result
            else:
                return None
        
        return None

    def FindPageByName(self, pages : Pages[Page], target : str) -> Pages[Page]:

        for page in pages:

            if page.contents:
                for content in page.contents:
                    
                    if content == target or content == "*":
                        return [page]

                    elif content[-2:] == ".*":
                        if target.startswith(content[:-2]):
                            return [page]
                            
                    elif content == "*":
                        return

            if len(page.children) > 0:
                result = self.FindPageByName(page.children, target)
                if result: return [page] + result
        return None
        
    def FindTargetPageURL(self, obj: docspec.ApiObject, target : docspec.ApiObject) -> t.Optional[str]:
        
        obj_id = self.GetObjectID(obj)
        target_id = self.GetObjectID(target)

        this_page = self.FindPageByName(self.pages, obj_id)
        target_page = self.FindPageByName(self.pages, target_id)

        if target_page == None or this_page == None: return None

        for parent_index in range(len(this_page)):
                if parent_index >= len(target_page): break
                if this_page[parent_index] != target_page[parent_index]:
                        parent_index -= 1
                        break
        
        parent_index += 1
        
        relative_path = "../" * (len(this_page) - parent_index)
        url = relative_path + "/".join(page.title.replace(" ", "-").lower() for page in target_page[parent_index:]) + "#" + target_id
        
        return url

    def resolve_ref(self,
                    obj        : docspec.ApiObject,
                    reference  : str,
                    typeFilter : t.List[t.Type[docspec.ApiObject]] = []
        ) -> t.Optional[t.Tuple[str, docspec.ApiObject]]:
        
        refNames = reference.split(".")
        targetURL = None

        # look for the reference in the local module
        if self.renderer.crossref_local:
            result = self.FindRefLocal(obj, refNames, typeFilter)
            if result: targetURL = self.FindTargetPageURL(obj, result)
        
        if targetURL: return targetURL

        # look for the reference in all of the imported modules
        if self.renderer.crossref_import:
            result = self.FindRefFromImport(obj, refNames, typeFilter)
            if result: targetURL = self.FindTargetPageURL(obj, result)
        
        if targetURL: return targetURL

        # look for the reference in all of the project modules
        if self.renderer.crossref_global:
            easyResults, hardResults = self.FindAllReference(obj, refNames, typeFilter)
            
            # hardResults is the top matches
            for result in hardResults:
                targetURL = self.FindTargetPageURL(obj, result)
                if targetURL: return targetURL

            for result in easyResults:
                targetURL = self.FindTargetPageURL(obj, result)
                if targetURL: return targetURL

        return None


class ImportInfo(object):

    def __init__(self, owner: SmartReferenceResolver, currentModule : docspec.Module, _import : docspec.Indirection) -> None:
        
        dotCount = len(_import.target) - len(_import.target.lstrip('.'))
        hasRelativeImport = dotCount > 0
        relativeCount = dotCount
            
        isImportAll = _import.name == "*"

        if isImportAll: importPaths = _import.target[dotCount:].split('.')[:-1]
        else: importPaths = _import.target[dotCount:].split('.')
        
        importedModuleName = importPaths[-1]
        isImportAs = (not isImportAll) and (importedModuleName != _import.name)

        isImportAsNested = isImportAs and len(importPaths) > 1
        
        if isImportAll:
            relativeCount -= 1
        elif isImportAs:
            relativeCount -= 1
            if isImportAsNested: relativeCount += 1
        
        if hasRelativeImport and not isImportAll: relativeCount -= 1 # no idea why

        self.owner = owner

        # if filename == "__init__.py" then the currentModule.name is the directory
        # else it is a file path, so we have to strip it
        if os.path.basename(currentModule.location.filename) == "__init__.py":
            currentPaths = currentModule.name.split(".")
        else:
            currentPaths = currentModule.name.split(".")[:-1]

        self.parentPath = currentPaths[:len(currentPaths) - relativeCount]

        
        self.relativeCount = relativeCount
        self.isImportAs = isImportAs
        self.isImportAll = isImportAll
        self.isImportModule = None

        self.importedObjects = []
        self.importAsName = _import.name
        self.importPaths = importPaths
        self.importedFrom = currentModule
        self.module = None
        
        absoluteImportPath = ".".join(self.parentPath + self.importPaths)


    def Process(self) -> bool:
        
        # from ..program.run import walk
        # will try to find ..\program\run\walk first
        #             then ..\program\run
        #             then ..\program
        #
        # if we found it in the first try, it is a module
        # if not then it is class, object,...

        for tries in range(len(self.importPaths)):
            tryName = self.importPaths[:len(self.importPaths) - tries]
            absoluteImportPath = ".".join(self.parentPath + tryName)

            foundModule = self.owner.FindModuleByName(absoluteImportPath)

            if foundModule and foundModule != self.importedFrom:
                # if we found it at ..\program
                # then importedObjects is [run, walk]
                # and isImportModule is False
                self.importedObjects = self.importPaths[len(self.importPaths) - tries:]
                self.isImportModule = tries == 0
                self.module = foundModule
                
                return True
            
            # absoluteImportPath for import all (from ..program.run import *)
            # is always the path to a module, not objects
            # if we run into this code then the imported module doesn't exists (?)
            # if self.isImportAll:
                # raise FileNotFoundError("The imported module: {} is invalid".format(self.parentPath + self.importPaths))
                
        # raise FileNotFoundError("The imported module: {} is invalid".format(self.parentPath + self.importPaths))
        return False



