import React, { useMemo, useState } from "react";
import {
  Card,
  CardHeader,
  CardContent,
  Tabs,
  Tab,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Tooltip,
  Chip,
  TableContainer,
  Stack,
  Typography,
  Paper
} from "@mui/material";

const chipColors = action => {
  if (!action) return { color: "default", label: "" };
  if (action.startsWith("shift")) return { color: "primary", label: action };
  if (action.startsWith("reduce")) return { color: "secondary", label: action };
  if (action === "accept") return { color: "success", label: action };
  return { color: "default", label: action };
};

function Legend() {
  return (
    <Stack direction="row" spacing={1} flexWrap="wrap">
      <Chip size="small" label="Shift" color="primary" />
      <Chip size="small" label="Reduce" color="secondary" />
      <Chip size="small" label="Accept" color="success" />
      <Chip size="small" label="Conflict" color="error" />
    </Stack>
  );
}

function ActionGotoTable({ actionTable, gotoTable, conflicts }) {
  const [tab, setTab] = useState(0);
  const conflictKeys = useMemo(() => {
    return new Set(
      (conflicts || []).map(conflict => `${conflict.state}|${conflict.symbol}`)
    );
  }, [conflicts]);

  if (!actionTable || !Object.keys(actionTable).length) return null;
  const states = Object.keys(actionTable);
  const terminals = Array.from(
    new Set(states.flatMap(st => Object.keys(actionTable[st])))
  );
  const nonterminals = Array.from(
    new Set(states.flatMap(st => Object.keys(gotoTable?.[st] || {})))
  );

  const renderActionCell = (state, terminal) => {
    const action = actionTable?.[state]?.[terminal];
    if (!action) return null;
    const { color, label } = chipColors(action);
    const isConflict = conflictKeys.has(`${state}|${terminal}`);

    return (
      <Tooltip title={`ACTION(${state}, ${terminal}) = ${label}`}>
        <Chip
          size="small"
          label={label}
          color={isConflict ? "error" : color}
          variant={isConflict ? "filled" : "outlined"}
          sx={{ fontWeight: 600 }}
        />
      </Tooltip>
    );
  };

  const renderGotoCell = (state, nt) => {
    const value = gotoTable?.[state]?.[nt];
    if (value === undefined || value === null) return null;
    return (
      <Tooltip title={`GOTO(${state}, ${nt}) = ${value}`}>
        <Chip size="small" label={value} color="info" variant="outlined" />
      </Tooltip>
    );
  };

  return (
    <Card elevation={3} sx={{ borderRadius: 3 }}>
      <CardHeader
        title="PARSING TABLE"
       
        action={<Legend />}
      />
      <CardContent>
        <Tabs
          value={tab}
          onChange={(_, value) => setTab(value)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ mb: 2 }}
        >
          <Tab label="ACTION Table" />
          <Tab label="GOTO Table" />
        </Tabs>

        {tab === 0 && (
          <Paper variant="outlined" sx={{ borderRadius: 3 }}>
            <TableContainer sx={{ maxHeight: 400 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ bgcolor: "grey.100" }}>State</TableCell>
                    {terminals.map(t => (
                      <TableCell key={`term-${t}`} sx={{ bgcolor: "grey.50" }}>
                        <Typography variant="caption">{t}</Typography>
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {states.map(state => (
                    <TableRow key={`action-${state}`} hover>
                      <TableCell>
                        <Typography fontWeight={600}>{state}</Typography>
                      </TableCell>
                      {terminals.map(t => (
                        <TableCell key={`${state}-${t}`}>
                          {renderActionCell(state, t)}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        )}

        {tab === 1 && (
          <Paper variant="outlined" sx={{ borderRadius: 3 }}>
            <TableContainer sx={{ maxHeight: 400 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ bgcolor: "grey.100" }}>State</TableCell>
                    {nonterminals.map(nt => (
                      <TableCell key={`nt-${nt}`} sx={{ bgcolor: "grey.50" }}>
                        <Typography variant="caption">{nt}</Typography>
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {states.map(state => (
                    <TableRow key={`goto-${state}`} hover>
                      <TableCell>
                        <Typography fontWeight={600}>{state}</Typography>
                      </TableCell>
                      {nonterminals.map(nt => (
                        <TableCell key={`${state}-${nt}`}>
                          {renderGotoCell(state, nt)}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        )}
      </CardContent>
    </Card>
  );
}

export default ActionGotoTable;
