import React from "react";
import {
  Card,
  CardHeader,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  Stack,
  Alert,
  Typography
} from "@mui/material";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";

function AmbiguityList({ title, items, emptyLabel, color, icon }) {
  if (!items?.length) {
    return (
      <Alert severity="info" variant="outlined" sx={{ my: 1 }}>
        {emptyLabel}
      </Alert>
    );
  }

  return (
    <>
      <Typography variant="subtitle2" sx={{ fontWeight: 600, mt: 2, mb: 1 }}>
        {title}
      </Typography>
      <List dense sx={{ borderRadius: 2, bgcolor: "grey.50", p: 0 }}>
        {items.map((item, idx) => (
          <ListItem
            key={`${title}-${idx}`}
            divider={idx !== items.length - 1}
            alignItems="flex-start"
          >
            <Stack spacing={1} sx={{ width: "100%" }}>
              <Stack direction="row" spacing={1} alignItems="center">
                <Chip
                  icon={icon}
                  label={`State ${item.state}`}
                  color={color}
                  size="small"
                  variant="outlined"
                />
                {item.symbol && (
                  <Chip
                    label={`Symbol "${item.symbol}"`}
                    color={color}
                    size="small"
                    variant="outlined"
                  />
                )}
                {item.type && <Chip label={item.type} size="small" />}
              </Stack>
              <ListItemText
                primaryTypographyProps={{ variant: "body2" }}
                primary={item.details || "No details provided"}
              />
            </Stack>
          </ListItem>
        ))}
      </List>
    </>
  );
}

function AmbiguityPanel({ ambiguity }) {
  if (!ambiguity) return null;

  return (
    <Card elevation={3} sx={{ borderRadius: 3 }}>
      <CardHeader
        title="Ambiguity & Conflict Insights"
        subheader="Review conflicts and how the analyzer resolved them."
      />
      <Divider />
      <CardContent>
        <Stack spacing={2}>
          {ambiguity.has_conflict ? (
            <Alert severity="warning" icon={<WarningAmberIcon />}>
              Conflicts detected in the grammar. Review the list below.
            </Alert>
          ) : (
            <Alert severity="success" icon={<CheckCircleIcon />}>
              No LR(1) conflicts detected in the current grammar.
            </Alert>
          )}
          <AmbiguityList
            title="Ambiguity Conflicts"
            items={ambiguity.conflicts || []}
            emptyLabel="Great news — no conflicts reported."
            color="warning"
            icon={<WarningAmberIcon fontSize="small" />}
          />
          <AmbiguityList
            title="Resolved Conflicts"
            items={ambiguity.resolved_conflicts || []}
            emptyLabel="No resolved conflicts to display yet."
            color="success"
            icon={<CheckCircleIcon fontSize="small" />}
          />
        </Stack>
      </CardContent>
    </Card>
  );
}

export default AmbiguityPanel;

