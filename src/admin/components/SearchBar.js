const { TextField, InputAdornment } = MaterialUI;

export function SearchBar({ value, onChange }) {
    return (
        <TextField
            placeholder="Search customers..."
            value={value}
            onChange={onChange}
            variant="outlined"
            size="small"
            fullWidth
            InputProps={{
                startAdornment: (
                    <InputAdornment position="start">
                        <MaterialUI.Icon>search</MaterialUI.Icon>
                    </InputAdornment>
                ),
            }}
        />
    );
} 