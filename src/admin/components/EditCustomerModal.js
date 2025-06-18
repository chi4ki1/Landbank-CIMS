const {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Grid,
    CircularProgress
} = MaterialUI;

export function EditCustomerModal({ open, customer, onClose, onSave }) {
    const [formData, setFormData] = React.useState({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        dateOfBirth: '',
        status: 'Active',
        address: {
            street: '',
            city: '',
            state: '',
            zipCode: ''
        }
    });
    const [loading, setLoading] = React.useState(false);
    const [errors, setErrors] = React.useState({});

    React.useEffect(() => {
        if (customer) {
            setFormData({
                firstName: customer.firstName || '',
                lastName: customer.lastName || '',
                email: customer.email || '',
                phone: customer.phone || '',
                dateOfBirth: customer.dateOfBirth || '',
                status: customer.status || 'Active',
                address: customer.address || {
                    street: '',
                    city: '',
                    state: '',
                    zipCode: ''
                }
            });
        } else {
            setFormData({
                firstName: '',
                lastName: '',
                email: '',
                phone: '',
                dateOfBirth: '',
                status: 'Active',
                address: {
                    street: '',
                    city: '',
                    state: '',
                    zipCode: ''
                }
            });
        }
    }, [customer]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        if (name.includes('.')) {
            const [parent, child] = name.split('.');
            setFormData(prev => ({
                ...prev,
                [parent]: {
                    ...prev[parent],
                    [child]: value
                }
            }));
        } else {
            setFormData(prev => ({
                ...prev,
                [name]: value
            }));
        }
    };

    const validateForm = () => {
        const newErrors = {};
        if (!formData.firstName) newErrors.firstName = 'First name is required';
        if (!formData.lastName) newErrors.lastName = 'Last name is required';
        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Email is invalid';
        }
        if (!formData.phone) {
            newErrors.phone = 'Phone is required';
        } else if (!/^\d{10}$/.test(formData.phone.replace(/\D/g, ''))) {
            newErrors.phone = 'Phone number must be 10 digits';
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        setLoading(true);
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            onSave();
        } catch (error) {
            setErrors({ submit: 'Failed to save customer' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>
                {customer ? 'Edit Customer' : 'Add New Customer'}
            </DialogTitle>
            <form onSubmit={handleSubmit}>
                <DialogContent>
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="First Name"
                                name="firstName"
                                value={formData.firstName}
                                onChange={handleChange}
                                error={!!errors.firstName}
                                helperText={errors.firstName}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Last Name"
                                name="lastName"
                                value={formData.lastName}
                                onChange={handleChange}
                                error={!!errors.lastName}
                                helperText={errors.lastName}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Email"
                                name="email"
                                type="email"
                                value={formData.email}
                                onChange={handleChange}
                                error={!!errors.email}
                                helperText={errors.email}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Phone"
                                name="phone"
                                value={formData.phone}
                                onChange={handleChange}
                                error={!!errors.phone}
                                helperText={errors.phone}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Date of Birth"
                                name="dateOfBirth"
                                type="date"
                                value={formData.dateOfBirth}
                                onChange={handleChange}
                                InputLabelProps={{ shrink: true }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <FormControl fullWidth>
                                <InputLabel>Status</InputLabel>
                                <Select
                                    name="status"
                                    value={formData.status}
                                    onChange={handleChange}
                                    label="Status"
                                >
                                    <MenuItem value="Active">Active</MenuItem>
                                    <MenuItem value="Pending">Pending</MenuItem>
                                    <MenuItem value="Inactive">Inactive</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Street Address"
                                name="address.street"
                                value={formData.address.street}
                                onChange={handleChange}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="City"
                                name="address.city"
                                value={formData.address.city}
                                onChange={handleChange}
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                fullWidth
                                label="State"
                                name="address.state"
                                value={formData.address.state}
                                onChange={handleChange}
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                fullWidth
                                label="ZIP Code"
                                name="address.zipCode"
                                value={formData.address.zipCode}
                                onChange={handleChange}
                            />
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={onClose}>Cancel</Button>
                    <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        disabled={loading}
                    >
                        {loading ? <CircularProgress size={24} /> : 'Save Changes'}
                    </Button>
                </DialogActions>
            </form>
        </Dialog>
    );
} 