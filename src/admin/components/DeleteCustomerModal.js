const {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Typography,
    Box,
    CircularProgress
} = MaterialUI;

export function DeleteCustomerModal({ open, customer, onClose, onConfirm }) {
    const [loading, setLoading] = React.useState(false);

    const handleDelete = async () => {
        if (!customer) return;
        
        setLoading(true);
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            onConfirm();
        } catch (error) {
            console.error('Failed to delete customer:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle>
                <Box display="flex" alignItems="center" gap={1}>
                    <MaterialUI.Icon color="error">warning</MaterialUI.Icon>
                    Confirm Deletion
                </Box>
            </DialogTitle>
            <DialogContent>
                <Typography variant="body1" paragraph>
                    Are you sure you want to permanently delete {customer?.fullName}? This action cannot be undone.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                    Customer ID: {customer?.id}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                    Email: {customer?.email}
                </Typography>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} disabled={loading}>
                    Cancel
                </Button>
                <Button
                    onClick={handleDelete}
                    color="error"
                    variant="contained"
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <MaterialUI.Icon>delete</MaterialUI.Icon>}
                >
                    Delete Customer
                </Button>
            </DialogActions>
        </Dialog>
    );
} 