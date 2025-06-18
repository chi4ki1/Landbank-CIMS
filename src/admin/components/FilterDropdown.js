const { FormControl, Select, MenuItem, InputLabel, TextField } = MaterialUI;

export function FilterDropdown({ statusFilter, onStatusChange, dateFilter, onDateChange }) {
    return (
        <div style={{ display: 'flex', gap: '16px' }}>
            <FormControl size="small" style={{ minWidth: 120 }}>
                <InputLabel>Status</InputLabel>
                <Select
                    value={statusFilter}
                    onChange={(e) => onStatusChange(e.target.value)}
                    label="Status"
                >
                    <MenuItem value="all">All</MenuItem>
                    <MenuItem value="Active">Active</MenuItem>
                    <MenuItem value="Pending">Pending</MenuItem>
                    <MenuItem value="Inactive">Inactive</MenuItem>
                </Select>
            </FormControl>

            <TextField
                label="Registration Date"
                type="date"
                value={dateFilter || ''}
                onChange={(e) => onDateChange(e.target.value ? new Date(e.target.value) : null)}
                size="small"
                InputLabelProps={{ shrink: true }}
            />
        </div>
    );
} 