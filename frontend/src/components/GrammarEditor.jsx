import React, { useMemo } from "react";
import {
  Card,
  CardHeader,
  CardContent,
  CardActions,
  Stack,
  TextField,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Button,
  Tooltip,
  Chip,
  Divider,
} from "@mui/material";
import PlayCircleOutlineIcon from "@mui/icons-material/PlayCircleOutline";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import CodeMirror from "@uiw/react-codemirror";
import { javascript } from "@codemirror/lang-javascript";
import { keymap } from "@codemirror/view";
import { EditorView } from "@codemirror/view";

const GRAMMAR_PLACEHOLDER =
  "Paste your context-free grammar, one production per line (e.g. S -> S a | b)";

function GrammarEditor({
  grammarText,
  setGrammarText,
  startSymbol,
  setStartSymbol,
  options,
  setOptions,
  onAnalyze,
  isAnalyzing,
}) {
  const isDisabled = !grammarText.trim() || isAnalyzing;
  const editorExtensions = useMemo(
    () => [
      javascript(),
      keymap.of([
        {
          key: "Mod-Enter",
          preventDefault: true,
          run: () => {
            onAnalyze();
            return true;
          }
        }
      ]),
      EditorView.lineWrapping
    ],
    [onAnalyze]
  );

  return (
    <Card elevation={4} sx={{ borderRadius: 3 }}>
      <CardHeader
        title="INPUT GRAMMAR"
        subheader="Edit your grammar, define the start symbol, then run analyser."
      />
      <Divider />
      <CardContent sx={{ pt: 3 }}>
        <Stack spacing={2}>
          <CodeMirror
            value={grammarText}
            height="280px"
            extensions={editorExtensions}
            onChange={value => setGrammarText(value)}
            basicSetup={{
              foldGutter: false,
              highlightActiveLine: false
            }}
            placeholder={GRAMMAR_PLACEHOLDER}
          />
          <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
            <TextField
              label="Start symbol"
              value={startSymbol}
              onChange={e => setStartSymbol(e.target.value)}
              fullWidth
            />
          </Stack>
        </Stack>
      </CardContent>
      <Divider />
      <CardActions sx={{ justifyContent: "flex-start", p: 3 }}>
        <Tooltip title="Run standard grammar analysis">
          <span>
            <Button
              variant="contained"
              startIcon={<PlayCircleOutlineIcon />}
              onClick={onAnalyze}
              disabled={isDisabled}
            >
              Analyze Grammar
            </Button>
          </span>
        </Tooltip>
      </CardActions>
    </Card>
  );
}

export default GrammarEditor;
