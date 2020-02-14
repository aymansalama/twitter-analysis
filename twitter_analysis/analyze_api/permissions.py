from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    " Custom permission to only allow owner of the object to edit it"
    
    def has_object_permission(self, request, view, obj):
        #read permissions are allowed to any request
        #so GET, HEAD and OPTIONS request will always be allowed 

        if request.method in permissions.SAFE_METHODS:
            return True
        
        #Write permissions are only allowed to the owner of the snippet
        return obj.user == request.user