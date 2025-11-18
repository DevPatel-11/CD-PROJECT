import React from "react";
import {
  Card,
  CardHeader,
  CardContent,
  Grid,
  Paper,
  Stack,
  Chip,
  Typography
} from "@mui/material";

function SetChips({ label, items }) {
  if (!items?.length) {
    return <Typography variant="body2" color="text.secondary">–</Typography>;
  }

  return (
    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
      {items.map(sym => (
        <Chip key={`${label}-${sym}`} label={sym} size="small" color="primary" variant="outlined" />
      ))}
    </Stack>
  );
}

function FirstFollowTable({ first, follow }) {
  const nts = Array.from(new Set([...Object.keys(first || {}), ...Object.keys(follow || {})]));
  if (!nts.length) return null;

  return (
    <Card elevation={3} sx={{ borderRadius: 3 }}>
      <CardHeader
        title="FIRST AND FOLLOW SETS"
        
      />
      <CardContent>
        <Grid container spacing={2}>
          {nts.map(nt => (
            <Grid item xs={12} md={6} lg={4} key={nt}>
              <Paper elevation={0} sx={{ p: 2, borderRadius: 3, bgcolor: "grey.50" }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                  {nt}
                </Typography>
                <Typography variant="overline" color="text.secondary">First</Typography>
                <SetChips label={`first-${nt}`} items={first?.[nt]} />
                <Typography variant="overline" color="text.secondary" sx={{ mt: 1, display: "block" }}>
                  Follow
                </Typography>
                <SetChips label={`follow-${nt}`} items={follow?.[nt]} />
              </Paper>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
}

export default FirstFollowTable;
