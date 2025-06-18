const { useState, useEffect } = React;
const { 
    Container, 
    Paper, 
    Typography, 
    Button, 
    Box,
    CircularProgress,
    Snackbar,
    Alert
} = MaterialUI;

export function App() {
    const [customers, setCustomers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [rowsPerPage] = useState(10);
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [dateFilter, setDateFilter] = useState(null);
    const [selectedCustomer, setSelectedCustomer] = useState(null);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
    const [toast, setToast] = useState({ open: false, message: '', severity: 'success' });

    // Mock data for development
    const mockCustomers = [
        {
            id: 1,
            firstName: 'John',
            lastName: 'Doe',
            fullName: 'John Doe',
            email: 'john.doe@example.com',
            phone: '1234567890',
            status: 'Active',
            registrationDate: '2024-01-01',
            dateOfBirth: '1990-01-01',
            address: {
                street: '123 Main St',
                city: 'Manila',
                state: 'NCR',
                zipCode: '1000'
            }
        },
        {
            id: 2,
            firstName: 'Jane',
            lastName: 'Smith',
            fullName: 'Jane Smith',
            email: 'jane.smith@example.com',
            phone: '0987654321',
            status: 'Pending',
            registrationDate: '2024-01-02',
            dateOfBirth: '1992-02-02',
            address: {
                street: '456 Oak St',
                city: 'Quezon City',
                state: 'NCR',
                zipCode: '1100'
            }
        }
    ];

    // Fetch customers data
    const fetchCustomers = async () => {
        try {
            setLoading(true);
            // Simulate API call with mock data
            await new Promise(resolve => setTimeout(resolve, 1000));
            setCustomers(mockCustomers);
            setError(null);
        } catch (err) {
            setError('Failed to fetch customers');
            showToast('Failed to fetch customers', 'error');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCustomers();
    }, [page, statusFilter, dateFilter]);

    // Filter customers based on search query and filters
    const filteredCustomers = customers.filter(customer => {
        const matchesSearch = customer.fullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            customer.email.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesStatus = statusFilter === 'all' || customer.status === statusFilter;
        const matchesDate = !dateFilter || new Date(customer.registrationDate) >= dateFilter;
        return matchesSearch && matchesStatus && matchesDate;
    });

    // Pagination
    const paginatedCustomers = filteredCustomers.slice(
        (page - 1) * rowsPerPage,
        page * rowsPerPage
    );

    // Handle customer actions
    const handleEdit = (customer) => {
        setSelectedCustomer(customer);
        setIsEditModalOpen(true);
    };

    const handleDelete = (customer) => {
        setSelectedCustomer(customer);
        setIsDeleteModalOpen(true);
    };

    const handleStatusChange = async (customerId, newStatus) => {
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 500));
            setCustomers(prev => prev.map(customer => 
                customer.id === customerId 
                    ? { ...customer, status: newStatus }
                    : customer
            ));
            showToast('Status updated successfully', 'success');
        } catch (err) {
            showToast('Failed to update status', 'error');
        }
    };

    const showToast = (message, severity) => {
        setToast({ open: true, message, severity });
    };

    const handleCloseToast = () => {
        setToast({ ...toast, open: false });
    };

    if (loading) {
        return (
            <Box className="loading-spinner">
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Container>
                <Alert severity="error">{error}</Alert>
            </Container>
        );
    }

    return (
        <Container className="admin-container">
            <Paper className="dashboard-header">
                <Typography variant="h4" component="h1">
                    Customer Management
                </Typography>
                <Box className="search-filter-container">
                    <SearchBar 
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    <FilterDropdown
                        statusFilter={statusFilter}
                        onStatusChange={setStatusFilter}
                        dateFilter={dateFilter}
                        onDateChange={setDateFilter}
                    />
                    <Button
                        variant="contained"
                        color="primary"
                        startIcon={<MaterialUI.Icon>refresh</MaterialUI.Icon>}
                        onClick={fetchCustomers}
                    >
                        Refresh
                    </Button>
                    <Button
                        variant="contained"
                        color="primary"
                        startIcon={<MaterialUI.Icon>add</MaterialUI.Icon>}
                        onClick={() => {
                            setSelectedCustomer(null);
                            setIsEditModalOpen(true);
                        }}
                    >
                        Add Customer
                    </Button>
                </Box>
            </Paper>

            <CustomerTable
                customers={paginatedCustomers}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onStatusChange={handleStatusChange}
                page={page}
                rowsPerPage={rowsPerPage}
                totalCount={filteredCustomers.length}
                onPageChange={setPage}
            />

            <EditCustomerModal
                open={isEditModalOpen}
                customer={selectedCustomer}
                onClose={() => setIsEditModalOpen(false)}
                onSave={() => {
                    setIsEditModalOpen(false);
                    fetchCustomers();
                    showToast('Customer saved successfully', 'success');
                }}
            />

            <DeleteCustomerModal
                open={isDeleteModalOpen}
                customer={selectedCustomer}
                onClose={() => setIsDeleteModalOpen(false)}
                onConfirm={() => {
                    setIsDeleteModalOpen(false);
                    fetchCustomers();
                    showToast('Customer deleted successfully', 'success');
                }}
            />

            <Snackbar
                open={toast.open}
                autoHideDuration={6000}
                onClose={handleCloseToast}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
                <Alert onClose={handleCloseToast} severity={toast.severity}>
                    {toast.message}
                </Alert>
            </Snackbar>
        </Container>
    );
} 