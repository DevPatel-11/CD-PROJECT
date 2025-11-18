import React, { useMemo, useState } from "react";
import {
  Card,
  CardHeader,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
  Snackbar,
  Alert,
  Box,
  TextField,
  Stack,
  Chip,
  InputAdornment
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import SearchIcon from "@mui/icons-material/Search";

function formatItem(item) {
  return `${item.production} [dot=${item.dot}] [lookahead=${item.lookahead}]`;
}

function LR1ItemSets({ lr1ItemSets }) {
  const [copiedIdx, setCopiedIdx] = useState(-1);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [query, setQuery] = useState("");

  const filteredSets = useMemo(() => {
    if (!query.trim()) return lr1ItemSets || [];
    return (lr1ItemSets || []).filter(set =>
      set.items.some(item => formatItem(item).toLowerCase().includes(query.toLowerCase()))
    );
  }, [lr1ItemSets, query]);

  const handleCopy = (itemText, idx) => {
    navigator.clipboard.writeText(itemText);
    setCopiedIdx(idx);
    setSnackbarOpen(true);
    setTimeout(() => setCopiedIdx(-1), 800);
  };

  if (!filteredSets.length) return null;

  return (
    <Card elevation={3} sx={{ borderRadius: 3 }}>
      <CardHeader
        title="LR(1) ITEM SETS"
        
      />
      <CardContent>
        <Stack spacing={2}>
          <TextField
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search states, productions, lookaheads..."
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: "text.secondary" }} />
                </InputAdornment>
              )
            }}
            fullWidth
          />
          {filteredSets.map(set => (
            <Accordion key={set.id} disableGutters sx={{ borderRadius: 2, border: "1px solid", borderColor: "grey.200" }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                  <Typography variant="subtitle1">State {set.id}</Typography>
                  <Chip label={`${set.items.length} items`} size="small" />
                </Stack>
              </AccordionSummary>
              <AccordionDetails>
                <List dense sx={{ maxHeight: 240, overflowY: "auto" }}>
                  {set.items.map((item, idx) => {
                    const itemText = formatItem(item);
                    const parts = item.production.split(" ");
                    return (
                      <ListItem
                        key={`${set.id}-${idx}`}
                        divider
                        secondaryAction={
                          <Tooltip title="Copy item">
                            <IconButton edge="end" onClick={() => handleCopy(itemText, idx)} size="small">
                              <ContentCopyIcon
                                fontSize="small"
                                color={copiedIdx === idx ? "success" : "action"}
                              />
                            </IconButton>
                          </Tooltip>
                        }
                      >
                        <ListItemText
                          primary={
                            <Box component="span" sx={{ display: "inline-flex", flexWrap: "wrap", gap: 0.5 }}>
                              {parts.map((sym, i) => (
                                <React.Fragment key={`${sym}-${i}`}>
                                  {i === item.dot + 2 && <strong style={{ color: "#5664d2" }}>•</strong>}
                                  <span>{sym}</span>
                                </React.Fragment>
                              ))}
                              {item.dot === parts.length - 2 && <strong style={{ color: "#5664d2" }}>•</strong>}
                              <Chip
                                label={`lookahead: ${item.lookahead}`}
                                size="small"
                                color="info"
                                variant="outlined"
                                sx={{ ml: 1 }}
                              />
                            </Box>
                          }
                        />
                      </ListItem>
                    );
                  })}
                </List>
              </AccordionDetails>
            </Accordion>
          ))}
        </Stack>
      </CardContent>
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={1000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert severity="success" sx={{ width: "100%" }}>
          LR(1) item copied!
        </Alert>
      </Snackbar>
    </Card>
  );
}

export default LR1ItemSets;
