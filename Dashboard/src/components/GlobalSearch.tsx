import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  CircularProgress,
  ClickAwayListener,
  Divider,
  InputAdornment,
  List,
  ListItemButton,
  ListItemText,
  ListSubheader,
  Paper,
  Popper,
  TextField,
  Typography
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { apiService } from '../services/apiService';
import type { GlobalSearchResults, SearchResultItem } from '../types';

const MIN_QUERY_LENGTH = 2;
const DEBOUNCE_MS = 300;

const CATEGORY_CONFIG: Array<{ key: keyof GlobalSearchResults; label: string; route: string }> = [
  { key: 'locomotives', label: 'Locomotives', route: '/locomotives' },
  { key: 'equipment', label: 'Equipment', route: '/equipment' },
  { key: 'sections', label: 'Sections', route: '/sections' },
  { key: 'users', label: 'Users', route: '/users' },
  { key: 'checksheets', label: 'Checksheets', route: '/checksheets' },
  { key: 'templates', label: 'Templates', route: '/templates' }
];

export default function GlobalSearch() {
  const navigate = useNavigate();
  const anchorRef = useRef<HTMLDivElement | null>(null);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<GlobalSearchResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const trimmed = query.trim();

    if (trimmed.length < MIN_QUERY_LENGTH) {
      setResults(null);
      setError(null);
      setLoading(false);
      setOpen(false);
      return;
    }

    setLoading(true);
    const timer = window.setTimeout(() => {
      apiService
        .globalSearch(trimmed)
        .then((res) => {
          setResults(res.data);
          setError(null);
          setOpen(true);
        })
        .catch(() => {
          setResults(null);
          setError('Unable to search right now. Please try again.');
          setOpen(true);
        })
        .finally(() => setLoading(false));
    }, DEBOUNCE_MS);

    return () => window.clearTimeout(timer);
  }, [query]);

  const visibleCategories = useMemo(
    () => CATEGORY_CONFIG.filter((category) => (results?.[category.key].length ?? 0) > 0),
    [results]
  );

  const handleSelect = (route: string, item: SearchResultItem) => {
    setOpen(false);
    setQuery('');
    setResults(null);
    navigate(`${route}?id=${encodeURIComponent(item.nav_key)}`);
  };

  return (
    <ClickAwayListener onClickAway={() => setOpen(false)}>
      <Box ref={anchorRef} sx={{ position: 'relative', flexGrow: 1, maxWidth: 480, mx: { xs: 1, md: 3 } }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search locomotives, equipment, users, checksheets..."
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onFocus={() => {
            if (results || error) setOpen(true);
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" sx={{ color: 'text.secondary' }} />
              </InputAdornment>
            ),
            endAdornment: loading ? (
              <InputAdornment position="end">
                <CircularProgress size={16} />
              </InputAdornment>
            ) : null
          }}
        />

        <Popper
          open={open}
          anchorEl={anchorRef.current}
          placement="bottom-start"
          style={{ zIndex: 1300, width: anchorRef.current?.clientWidth }}
        >
          <Paper elevation={6} sx={{ mt: 0.5, maxHeight: 420, overflow: 'auto' }}>
            {error ? (
              <Box sx={{ p: 2 }}>
                <Typography color="error.main" variant="body2">{error}</Typography>
              </Box>
            ) : results && visibleCategories.length === 0 ? (
              <Box sx={{ p: 2 }}>
                <Typography color="text.secondary" variant="body2">No matching records found.</Typography>
              </Box>
            ) : results ? (
              <List dense disablePadding>
                {visibleCategories.map((category, index) => (
                  <Box key={category.key}>
                    <ListSubheader sx={{ bgcolor: 'background.paper', lineHeight: '32px' }}>
                      {category.label}
                    </ListSubheader>
                    {results[category.key].map((item) => (
                      <ListItemButton key={`${category.key}-${item.id}`} onClick={() => handleSelect(category.route, item)}>
                        <ListItemText primary={item.label} secondary={item.subtitle} />
                      </ListItemButton>
                    ))}
                    {index < visibleCategories.length - 1 ? <Divider /> : null}
                  </Box>
                ))}
              </List>
            ) : null}
          </Paper>
        </Popper>
      </Box>
    </ClickAwayListener>
  );
}
