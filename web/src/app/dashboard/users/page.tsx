'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AddUserModal } from '@/components/modals/add-user-modal'
import { EditUserModal } from '@/components/modals/edit-user-modal'
import { DeleteUserModal } from '@/components/modals/delete-user-modal'
import { ImportUsersModal } from '@/components/modals/import-users-modal'
import { exportUsersToCSV, exportSelectedUsersToCSV } from '@/lib/csv-export'
import { 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2,
  User,
  Mail,
  Shield,
  Clock,
  CheckCircle,
  XCircle,
  MoreVertical,
  UserPlus,
  Download,
  Upload,
  RefreshCw
} from 'lucide-react'

export default function UsersPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterRole, setFilterRole] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const [isLoading, setIsLoading] = useState(false)
  const [showAddUser, setShowAddUser] = useState(false)
  const [editingUser, setEditingUser] = useState(null)
  const [deletingUser, setDeletingUser] = useState(null)
  const [showImportModal, setShowImportModal] = useState(false)
  const [selectedUsers, setSelectedUsers] = useState<string[]>([])

  // Users data state
  const [users, setUsers] = useState([
    {
      id: '1',
      name: 'John Doe',
      email: 'john.doe@company.com',
      role: 'admin',
      status: 'active',
      lastLogin: '2024-01-15T10:30:00Z',
      avatar: null,
      permissions: ['read', 'write', 'admin']
    },
    {
      id: '2',
      name: 'Jane Smith',
      email: 'jane.smith@company.com',
      role: 'user',
      status: 'active',
      lastLogin: '2024-01-14T14:20:00Z',
      avatar: null,
      permissions: ['read', 'write']
    },
    {
      id: '3',
      name: 'Mike Johnson',
      email: 'mike.johnson@company.com',
      role: 'user',
      status: 'inactive',
      lastLogin: '2024-01-10T09:15:00Z',
      avatar: null,
      permissions: ['read']
    },
    {
      id: '4',
      name: 'Sarah Wilson',
      email: 'sarah.wilson@company.com',
      role: 'manager',
      status: 'active',
      lastLogin: '2024-01-15T08:45:00Z',
      avatar: null,
      permissions: ['read', 'write', 'approve']
    },
    {
      id: '5',
      name: 'David Brown',
      email: 'david.brown@company.com',
      role: 'user',
      status: 'pending',
      lastLogin: null,
      avatar: null,
      permissions: ['read']
    }
  ])

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRole = filterRole === 'all' || user.role === filterRole
    const matchesStatus = filterStatus === 'all' || user.status === filterStatus
    return matchesSearch && matchesRole && matchesStatus
  })

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800'
      case 'manager': return 'bg-blue-100 text-blue-800'
      case 'user': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getRoleText = (role: string) => {
    switch (role) {
      case 'admin': return 'Admin'
      case 'manager': return 'Manager'
      case 'user': return 'User'
      default: return role
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'inactive': return 'bg-gray-100 text-gray-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Active'
      case 'inactive': return 'Inactive'
      case 'pending': return 'Pending'
      default: return status
    }
  }

  // User management functions
  const handleAddUser = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setShowAddUser(true)
  }

  const handleUserAdded = (newUser: any) => {
    setUsers(prev => [...prev, newUser])
    setShowAddUser(false)
    console.log('✅ User added successfully:', newUser.name)
  }

  const handleEdit = (userId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const user = users.find(u => u.id === userId)
    setEditingUser(user)
  }

  const handleUserUpdated = (updatedUser: any) => {
    setUsers(prev => prev.map(user => 
      user.id === updatedUser.id ? updatedUser : user
    ))
    setEditingUser(null)
    console.log('✅ User updated successfully:', updatedUser.name)
  }

  const handleDelete = (userId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const user = users.find(u => u.id === userId)
    setDeletingUser(user)
  }

  const handleUserDeleted = (userId: string) => {
    setUsers(prev => prev.filter(user => user.id !== userId))
    setDeletingUser(null)
    console.log('✅ User deleted successfully')
  }

  const handleExport = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsLoading(true)
    try {
      exportUsersToCSV(filteredUsers, 'users-export.csv')
      console.log('✅ Users exported successfully')
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleImport = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setShowImportModal(true)
  }

  const handleUsersImported = (importedUsers: any[]) => {
    setUsers(prev => [...prev, ...importedUsers])
    setShowImportModal(false)
    console.log('✅ Users imported successfully:', importedUsers.length)
  }

  const handleRefresh = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsLoading(true)
    // Simulate refresh - in real app, this would fetch from API
    setTimeout(() => {
      setIsLoading(false)
      console.log('✅ Users data refreshed')
    }, 1000)
  }

  const handleBulkAction = (action: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (selectedUsers.length === 0) {
      console.log('Please select users first')
      return
    }

    setIsLoading(true)
    
    setTimeout(() => {
      switch (action) {
        case 'activate':
          setUsers(prev => prev.map(user => 
            selectedUsers.includes(user.id) 
              ? { ...user, status: 'active' }
              : user
          ))
          break
        case 'deactivate':
          setUsers(prev => prev.map(user => 
            selectedUsers.includes(user.id) 
              ? { ...user, status: 'inactive' }
              : user
          ))
          break
        case 'export':
          const selectedUsersData = users.filter(user => selectedUsers.includes(user.id))
          exportSelectedUsersToCSV(selectedUsersData, 'selected-users.csv')
          break
        case 'delete':
          setUsers(prev => prev.filter(user => !selectedUsers.includes(user.id)))
          setSelectedUsers([])
          break
      }
      setIsLoading(false)
      console.log(`✅ Bulk action "${action}" completed for ${selectedUsers.length} users`)
    }, 1000)
  }

  const handleFilterApply = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    console.log('✅ Filters applied')
  }

  const handleFilterClear = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setSearchTerm('')
    setFilterRole('all')
    setFilterStatus('all')
    setSelectedUsers([])
    console.log('✅ All filters cleared')
  }

  const handleMoreOptions = (user: any, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    console.log('✅ More options for:', user.name)
    // In a real app, this would show a context menu
  }

  const handleUserSelect = (userId: string, checked: boolean) => {
    if (checked) {
      setSelectedUsers(prev => [...prev, userId])
    } else {
      setSelectedUsers(prev => prev.filter(id => id !== userId))
    }
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedUsers(filteredUsers.map(user => user.id))
    } else {
      setSelectedUsers([])
    }
  }

  return (
    <>

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Users</h1>
            <p className="mt-2 text-gray-600">
              Manage team members and their permissions
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button 
              variant="outline" 
              onClick={handleRefresh}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button 
              variant="outline" 
              onClick={handleImport}
              className="flex items-center gap-2"
            >
              <Upload className="h-4 w-4" />
              Import
            </Button>
            <Button 
              variant="outline" 
              onClick={handleExport}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Export
            </Button>
            <Button 
              onClick={handleAddUser}
              className="flex items-center gap-2"
            >
              <UserPlus className="h-4 w-4" />
              Add User
            </Button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <div className="flex gap-2">
          <select
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            aria-label="Filter by role"
          >
            <option value="all">All Roles</option>
            <option value="admin">Admin</option>
            <option value="manager">Manager</option>
            <option value="user">User</option>
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            aria-label="Filter by status"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="pending">Pending</option>
          </select>
          <Button 
            variant="outline" 
            onClick={handleFilterApply}
            className="flex items-center gap-2"
          >
            <Filter className="h-4 w-4" />
            Apply Filters
          </Button>
          <Button 
            variant="outline" 
            onClick={handleFilterClear}
            className="flex items-center gap-2"
          >
            <XCircle className="h-4 w-4" />
            Clear
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Users</p>
                <p className="text-2xl font-bold text-gray-900">
                  {users.filter(u => u.status === 'active').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-gray-900">
                  {users.filter(u => u.status === 'pending').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <Shield className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Admins</p>
                <p className="text-2xl font-bold text-gray-900">
                  {users.filter(u => u.role === 'admin').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <User className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <p className="text-2xl font-bold text-gray-900">{users.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bulk Actions */}
      {filteredUsers.length > 0 && (
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">
              {filteredUsers.length} user{filteredUsers.length !== 1 ? 's' : ''} selected
            </span>
            <Button 
              variant="outline" 
              size="sm"
              onClick={(e) => handleBulkAction('activate', e)}
              className="flex items-center gap-2"
            >
              <CheckCircle className="h-4 w-4" />
              Activate
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={(e) => handleBulkAction('deactivate', e)}
              className="flex items-center gap-2"
            >
              <XCircle className="h-4 w-4" />
              Deactivate
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={(e) => handleBulkAction('export', e)}
              className="flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Export Selected
            </Button>
          </div>
        </div>
      )}

      {/* Users Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <input
                    id="select-all-users"
                    type="checkbox"
                    checked={selectedUsers.length === filteredUsers.length && filteredUsers.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-gray-300"
                    aria-label="Select all users"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Login
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Permissions
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUsers.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      id={`user-checkbox-${user.id}`}
                      type="checkbox"
                      checked={selectedUsers.includes(user.id)}
                      onChange={(e) => handleUserSelect(user.id, e.target.checked)}
                      className="rounded border-gray-300"
                      aria-label={`Select user ${user.name}`}
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                          <User className="h-5 w-5 text-gray-600" />
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {user.name}
                        </div>
                        <div className="text-sm text-gray-500 flex items-center">
                          <Mail className="h-3 w-3 mr-1" />
                          {user.email}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge className={getRoleColor(user.role)}>
                      {getRoleText(user.role)}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge className={getStatusColor(user.status)}>
                      {getStatusText(user.status)}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 text-gray-400 mr-1" />
                      {user.lastLogin 
                        ? new Date(user.lastLogin).toLocaleDateString()
                        : 'Never'
                      }
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center">
                      <Shield className="h-4 w-4 text-gray-400 mr-1" />
                      {user.permissions.length} permissions
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={(e) => handleEdit(user.id, e)}
                        title="Edit user"
                        className="hover:bg-blue-50 hover:text-blue-600"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={(e) => handleDelete(user.id, e)}
                        title="Delete user"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={(e) => handleMoreOptions(user, e)}
                        title="More options"
                        className="hover:bg-gray-50"
                      >
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Empty State */}
      {filteredUsers.length === 0 && (
        <div className="text-center py-12">
          <User className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No users found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || filterRole !== 'all' || filterStatus !== 'all'
              ? 'Try adjusting your search or filter criteria.'
              : 'Get started by adding a new user.'
            }
          </p>
          {(!searchTerm && filterRole === 'all' && filterStatus === 'all') && (
            <div className="mt-6">
              <Button 
                onClick={handleAddUser}
                className="flex items-center gap-2"
              >
                <UserPlus className="h-4 w-4" />
                Add User
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Modals */}
      <AddUserModal
        isOpen={showAddUser}
        onClose={() => setShowAddUser(false)}
        onUserAdded={handleUserAdded}
      />

      <EditUserModal
        isOpen={!!editingUser}
        onClose={() => setEditingUser(null)}
        onUserUpdated={handleUserUpdated}
        user={editingUser}
      />

      <DeleteUserModal
        isOpen={!!deletingUser}
        onClose={() => setDeletingUser(null)}
        onUserDeleted={handleUserDeleted}
        user={deletingUser}
      />

      <ImportUsersModal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        onUsersImported={handleUsersImported}
      />
    </>
  )
}