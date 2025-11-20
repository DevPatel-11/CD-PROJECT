import axios from "axios";

const BASE = "http://localhost:5000/api";

export async function analyzeGrammar({ grammarText, startSymbol, options }) {
  try {
    const resp = await axios.post(`${BASE}/analyze`, {
      grammar_text: grammarText,
      start_symbol: startSymbol,
      options: {
        detect_ambiguity: !!options.detectAmbiguity,
        build_slr: !!options.buildSLR
      }
    });
    return resp.data;
  } catch (e) {
    if (e.response && e.response.data && e.response.data.errors) {
      throw new Error((e.response.data.errors || []).join("; "));
    }
    throw e;
  }
}

export async function simulateParse({ grammarText, inputTokens, startSymbol, maxSteps }) {
  try {
    const resp = await axios.post(`${BASE}/simulate`, {
      grammar_text: grammarText,
      input_tokens: inputTokens,
      start_symbol: startSymbol,
      max_steps: maxSteps
    });
    return resp.data;
  } catch (e) {
    if (e.response && e.response.data && e.response.data.errors) {
      throw new Error((e.response.data.errors || []).join("; "));
    }
    throw e;
  }
}

