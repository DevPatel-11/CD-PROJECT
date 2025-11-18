import React, { useState } from "react";
import {
  Card,
  CardHeader,
  CardContent,
  Stack,
  TextField,
  Button,
  Grid,
  Alert,
  Chip,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider
} from "@mui/material";

function statusColor(status) {
  if (status === "accepted") return "success";
  if (status === "rejected") return "warning";
  if (!status) return "default";
  return "info";
}

function ParserSimulator({
  inputTokens,
  setInputTokens,
  onSimulate,
  maxSteps,
  setMaxSteps,
  parseResult,
  disabled,
  isSimulating
}) {
  const [showAll, setShowAll] = useState(true);

  return (
    <Card elevation={4} sx={{ borderRadius: 3 }}>
      <CardHeader
        title="PARSE SIMULATION"
        subheader="Test the LR(1) parser with custom tokens"
      />
      <CardContent>
        <Stack spacing={3}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={8}>
              <TextField
                label="Input tokens (space separated)"
                fullWidth
                value={inputTokens}
                onChange={e => setInputTokens(e.target.value)}
                onKeyDown={e => {
                  if ((e.metaKey || e.ctrlKey) && e.key === "Enter") onSimulate();
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                type="number"
                label="Max steps"
                fullWidth
                value={maxSteps}
                onChange={e => setMaxSteps(e.target.value)}
                inputProps={{ min: 1, max: 500 }}
              />
            </Grid>
          </Grid>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems="center">
            <Button
              variant="contained"
              size="large"
              onClick={onSimulate}
              disabled={disabled || isSimulating}
            >
              {isSimulating ? "Simulating..." : "Simulate Parsing"}
            </Button>
            {parseResult?.final_status && (
              <Chip
                label={`Status: ${parseResult.final_status}`}
                color={statusColor(parseResult.final_status)}
                variant="filled"
                sx={{ fontWeight: 600 }}
              />
            )}
          </Stack>

          {parseResult?.errors?.length > 0 && (
            <Alert severity="error">
              {parseResult.errors.map((err, idx) => (
                <div key={idx}>{err}</div>
              ))}
            </Alert>
          )}

          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  borderRadius: 3,
                  height: 420,
                  display: "flex",
                  flexDirection: "column"
                }}
              >
                <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="subtitle1">Simulation Steps</Typography>
                  {parseResult?.steps?.length > 1 && (
                    <Button size="small" onClick={() => setShowAll(x => !x)}>
                      {showAll ? "Show last step" : "Show all steps"}
                    </Button>
                  )}
                </Stack>
                <Divider />
                <List
                  dense
                  sx={{
                    flex: 1,
                    overflowY: "auto",
                    mt: 1
                  }}
                >
                  {(parseResult?.steps &&
                    (showAll
                      ? parseResult.steps
                      : [parseResult.steps[parseResult.steps.length - 1]]))?.map(step => (
                    <ListItem
                      key={step.step}
                      alignItems="flex-start"
                      sx={{ borderBottom: "1px solid", borderColor: "grey.100" }}
                    >
                      <ListItemText
                        primary={
                          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                            <Chip label={`Step ${step.step}`} size="small" color="primary" />
                            <Typography variant="body2" color="text.secondary">
                              Action: {step.action}
                            </Typography>
                          </Stack>
                        }
                        secondary={
                          <>
                            <Typography variant="caption" display="block">
                              Stack: {step.stack?.join(" ") || "–"}
                            </Typography>
                            <Typography variant="caption" display="block">
                              Input: {step.input?.join(" ") || "–"}
                            </Typography>
                            {step.notes && (
                              <Typography variant="caption" color="text.secondary" display="block">
                                Notes: {step.notes}
                              </Typography>
                            )}
                          </>
                        }
                      />
                    </ListItem>
                  )) || (
                    <ListItem>
                      <ListItemText primary="Run a simulation to see detailed steps." />
                    </ListItem>
                  )}
                </List>
              </Paper>
            </Grid>
          </Grid>
        </Stack>
      </CardContent>
    </Card>
  );
}

export default ParserSimulator;
