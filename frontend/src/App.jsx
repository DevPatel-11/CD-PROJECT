import React, { useMemo, useState } from "react";
import {
  ThemeProvider,
  createTheme
} from "@mui/material/styles";
import {
  CssBaseline,
  Container,
  Box,
  Stack,
  Typography,
  Snackbar,
  Alert
} from "@mui/material";
import GrammarEditor from "./components/GrammarEditor";
import FirstFollowTable from "./components/FirstFollowTable";
import LR1ItemSets from "./components/LR1ItemSets";
import ActionGotoTable from "./components/ActionGotoTable";
import ParserSimulator from "./components/ParserSimulator";
import AmbiguityPanel from "./components/AmbiguityPanel";
import { analyzeGrammar, simulateParse } from "./api";
import "./styles.css";

const gradientBackground = "linear-gradient(135deg, #f6f8fc 0%, #eef2ff 100%)";

function App() {
  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: "light",
          background: {
            default: "#f6f8fc"
          },
          primary: {
            main: "#5664d2"
          },
          secondary: {
            main: "#ff7f50"
          }
        },
        shape: {
          borderRadius: 16
        },
        typography: {
          fontFamily: `"Inter", "Segoe UI", sans-serif`,
          h4: {
            fontWeight: 700
          }
        }
      }),
    []
  );

  const [grammarText, setGrammarText] = useState("");
  const [startSymbol, setStartSymbol] = useState("");
  const [options, setOptions] = useState({ detectAmbiguity: true, buildLR1: true });
  const [analyzeResult, setAnalyzeResult] = useState(null);
  const [inputTokens, setInputTokens] = useState("");
  const [parseResult, setParseResult] = useState(null);
  const [maxSteps, setMaxSteps] = useState(20);
  const [error, setError] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);

  const runAnalyze = async (mode = "default") => {
    if (!grammarText.trim()) {
      setError("Please provide grammar rules before analyzing.");
      return;
    }

    const nextOptions = { ...options };
    if (mode === "lr1") nextOptions.buildLR1 = true;
    if (mode === "resolve") nextOptions.detectAmbiguity = true;
    setOptions(nextOptions);

    setIsAnalyzing(true);
    setParseResult(null);
    setError("");

    try {
      const res = await analyzeGrammar({
        grammarText,
        startSymbol: startSymbol || null,
        options: {
          detectAmbiguity: nextOptions.detectAmbiguity,
          buildLR1: nextOptions.buildLR1
        }
      });
      setAnalyzeResult(res);
    } catch (e) {
      setAnalyzeResult(null);
      setError(e?.message || "Error analyzing grammar.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSimulate = async () => {
    const tokens = inputTokens.trim().split(/\s+/).filter(Boolean);
    if (!tokens.length) {
      setError("Provide at least one input token to simulate the parser.");
      return;
    }

    setIsSimulating(true);
    setError("");

    try {
      const res = await simulateParse({
        grammarText,
        inputTokens: tokens,
        startSymbol: startSymbol || null,
        maxSteps: Math.max(1, Number(maxSteps) || 1)
      });
      setParseResult(res);

    } catch (e) {
      setParseResult(null);
      setError(e?.message || "Error simulating parser.");
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: "100vh", background: gradientBackground }}>
        <Container maxWidth="xl" sx={{ py: 5 }}>
          <Stack spacing={4}>
            <Box textAlign="center">
              <Typography variant="h4" gutterBottom>
                GRAMMAR AMBIGUITY CHECKER FOR LR(1)
              </Typography>
              <Typography color="text.secondary">
                Analyze grammar, construct parsing tables, resolves ambiguity and simulate LR(1) parses in a single workspace.
              </Typography>
            </Box>

            <Stack spacing={3}>
              <GrammarEditor
                grammarText={grammarText}
                setGrammarText={setGrammarText}
                startSymbol={startSymbol}
                setStartSymbol={setStartSymbol}
                options={options}
                setOptions={setOptions}
                onAnalyze={() => runAnalyze("default")}
                onGenerateLR1={() => runAnalyze("lr1")}
                onResolveAmbiguity={() => runAnalyze("resolve")}
                isAnalyzing={isAnalyzing}
              />
              {analyzeResult?.ambiguity && <AmbiguityPanel ambiguity={analyzeResult.ambiguity} />}
            </Stack>

            {analyzeResult && (
              <>
                <Stack spacing={3}>
                  <FirstFollowTable first={analyzeResult.first_sets} follow={analyzeResult.follow_sets} />
                  <LR1ItemSets lr1ItemSets={analyzeResult.lr1_item_sets} />
                  <ActionGotoTable
                    actionTable={analyzeResult.action_table}
                    gotoTable={analyzeResult.goto_table}
                    conflicts={analyzeResult.ambiguity?.conflicts}
                  />
                </Stack>
                <ParserSimulator
                  inputTokens={inputTokens}
                  setInputTokens={setInputTokens}
                  onSimulate={handleSimulate}
                  maxSteps={maxSteps}
                  setMaxSteps={setMaxSteps}
                  parseResult={parseResult}
                  disabled={!analyzeResult?.lr1_item_sets?.length}
                  isSimulating={isSimulating}
                />
              </>
            )}
          </Stack>
        </Container>
        <Snackbar
          open={!!error}
          autoHideDuration={4000}
          onClose={() => setError("")}
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        >
          <Alert severity="error" onClose={() => setError("")} sx={{ width: "100%" }}>
            {error}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App;
