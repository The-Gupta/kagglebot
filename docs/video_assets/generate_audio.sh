#!/bin/bash
# KaggleBot Demo Video - Seamless Audio (v2)
# Uses Samantha voice (most natural US English) with Amex Default Prediction
# Single continuous narration for seamless prosody.

VOICE="Samantha"
RATE=170
OUT_DIR="/Users/vishal/Downloads/kagglebot/docs/video_assets"
FULL_SCRIPT="$OUT_DIR/full_script.txt"
FULL_AUDIO="$OUT_DIR/full_narration.aiff"

mkdir -p "$OUT_DIR"

echo "Writing narration script (Amex Default Prediction)..."

cat > "$FULL_SCRIPT" << 'NARRATION'
KaggleBot. An AI powered Kaggle Competition Strategy Agent. Give it a competition URL, and it delivers a full analysis with working baseline code.

When you join a new Kaggle competition, you spend hours on discovery. Reading the competition overview. Downloading and profiling the dataset. Researching top discussions for insights. Writing boilerplate training code. KaggleBot automates the entire workflow.

Here is the architecture. It is a five agent pipeline built with Google A.D.K. The Orchestrator routes your request to four specialized agents. The Scraper Agent researches the competition page and discussions. The Data Agent profiles the dataset and detects quality issues. The Strategy Agent ranks M.L. approaches and presents them for your approval. That is the human in the loop gate. Then the Code Agent generates a secure, runnable baseline script.

Let me show you the live deployment. This is the KaggleBot chat UI, running on Google Cloud Run. The interface features a dark IDE-inspired theme with a pipeline sidebar showing all five agents.

Let us analyze the American Express Default Prediction competition. I paste the URL and the Scraper Agent starts researching. It extracts the competition title, type, evaluation metric, and pulls insights from top discussions about feature engineering strategies.

Next, the Data Agent profiles the dataset. It analyzes column types, detects missing values, identifies the target variable, and computes a data quality score. For Amex, it finds a large-scale tabular dataset with financial transaction features.

The Strategy Agent generates three ranked approaches. Number one, Gradient Boosted Trees with LightGBM. Number two, a deep tabular network. Number three, an ensemble of both. This is the Human in the Loop checkpoint. The user reviews the strategies and approves one before code generation begins.

The Code Agent generates a complete Python baseline. Notice the syntax highlighted code block with a copy button and a download button. Every line is security checked. No dangerous imports. No leaked API keys. The code is ready to run on Kaggle.

KaggleBot has three layers of security built in. Input validation blocks malicious URLs and path traversal. A secret scanner detects and redacts API keys. And A.S.T. analysis catches dangerous code patterns like subprocess calls and os dot system.

Every pipeline run produces a full observability trace. You can see each agent invocation, each tool call, timing in milliseconds, and the H.I.T.L. pause point. Full transparency into the agent pipeline.

In total, KaggleBot demonstrates eleven concepts from the Google Gen AI Intensive course. Six official concepts. A.D.K. for multi-agent systems. M.C.P. Servers for tool integration. Antigravity for development. Security with three layers. Deployability on Cloud Run. And Agent Skills for modular capabilities. Plus five bonus concepts. Observability with tracing. Evaluation with L.L.M. as judge. Cross-session memory. Session state management. And human in the loop controls.

The project is 43 files, over 5,000 lines of Python, 5 agents, 8 M.C.P. tools, and all 7 end-to-end tests pass.

KaggleBot. Five agents. Three M.C.P. servers. Eleven concepts. Built with Google A.D.K. and Antigravity IDE. The live demo and source code are linked in the description. Thanks for watching.
NARRATION

echo "Generating seamless narration with $VOICE at rate $RATE..."
say -v "$VOICE" -r $RATE -o "$FULL_AUDIO" < "$FULL_SCRIPT"

echo "Done!"
echo "Output: $FULL_AUDIO"
echo "Duration: $(afinfo "$FULL_AUDIO" 2>/dev/null | grep 'estimated duration' | awk '{print $3}')s"
