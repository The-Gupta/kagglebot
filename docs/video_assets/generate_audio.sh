#!/bin/bash
# KaggleBot Demo Video - Audio Generation Script
# Uses macOS 'say' to generate narration segments

VOICE="Aman"
RATE=165
OUT_DIR="/Users/vishal/Downloads/kagglebot/docs/video_assets"
mkdir -p "$OUT_DIR"

echo "Generating narration segments..."

# Segment 1: Hook (5s)
say -v "$VOICE" -r $RATE -o "$OUT_DIR/01_hook.aiff" \
"KaggleBot. An AI powered Kaggle Competition Strategy Agent. One command. Full competition analysis with working baseline code."

# Segment 2: Problem (8s)
say -v "$VOICE" -r $RATE -o "$OUT_DIR/02_problem.aiff" \
"When you join a new Kaggle competition, you spend four to eight hours just on discovery. Reading the overview. Profiling data. Researching discussions. Writing boilerplate code. KaggleBot automates all of that."

# Segment 3: Architecture (8s)
say -v "$VOICE" -r $RATE -o "$OUT_DIR/03_architecture.aiff" \
"It is a 5 agent system built with Google A.D.K. The Orchestrator routes to specialized agents. Scraper reads the competition. Data Agent profiles the dataset. Strategy Agent ranks M.L. approaches and waits for your approval. Then Code Agent generates secure baseline code."

# Segment 4: Demo - Scraper (5s)
say -v "$VOICE" -r $RATE -o "$OUT_DIR/04_scraper.aiff" \
"Let us analyze the Titanic competition. The Scraper Agent pulls competition metadata. Title, type, evaluation metric, and five discussion insights about feature engineering."

# Segment 5: Demo - Data (7s)
say -v "$VOICE" -r $RATE -o "$OUT_DIR/05_data.aiff" \
"The Data Agent profiles the dataset. 100 rows, 12 columns. Quality score 89 out of 100. It detects missing values and ID columns. The target variable Survived has a 61 to 39 percent class balance."

# Segment 6: Demo - Strategy (7s)
say -v "$VOICE" -r $RATE -o "$OUT_DIR/06_strategy.aiff" \
"Strategy Agent generates three ranked approaches. Number one, Logistic Regression for low effort. Number two, Gradient Boosting. Number three, Stacked Ensemble. This is the Human In The Loop gate. The user approves strategy number one."

# Segment 7: Demo - Code (5s)
say -v "$VOICE" -r $RATE -o "$OUT_DIR/07_code.aiff" \
"Code Agent generates 170 lines of runnable Python baseline. Every line is security checked. No dangerous imports. No leaked secrets. Safe equals true."

# Segment 8: Security (7s)
say -v "$VOICE" -r $RATE -o "$OUT_DIR/08_security.aiff" \
"Three layers of security. Input validation blocks malicious URLs and path traversal. Secret scanner detects and redacts A.P.I. keys. A.S.T. analysis catches dangerous code like subprocess and os dot system."

# Segment 9: Observability (6s)
say -v "$VOICE" -r $RATE -o "$OUT_DIR/09_observability.aiff" \
"Every pipeline run produces a full trace. You can see each agent, each tool call, timing in milliseconds, and the H.I.T.L. pause. Five agents. Ten tool calls. Total duration, 210 milliseconds."

# Segment 10: Concepts (5s)
say -v "$VOICE" -r $RATE -o "$OUT_DIR/10_concepts.aiff" \
"KaggleBot demonstrates all 6 official concepts. A.D.K., M.C.P. Servers, Antigravity, Security, Deployability, and Agent Skills. Plus 5 bonus concepts. Observability, Evaluation, Memory, Sessions, and H.I.T.L."

# Segment 11: Stats (5s)
say -v "$VOICE" -r $RATE -o "$OUT_DIR/11_stats.aiff" \
"43 files. 5239 lines of Python. 5 agents. 8 M.C.P. tools. 7 out of 7 end to end tests passing. 11 concepts total."

# Segment 12: Tests (5s)
say -v "$VOICE" -r $RATE -o "$OUT_DIR/12_tests.aiff" \
"All 7 end to end tests pass in under 2 seconds. Three competitions tested. Memory, Observability, Evaluation, and Agent Imports, all verified."

# Segment 13: Outro (5s)
say -v "$VOICE" -r $RATE -o "$OUT_DIR/13_outro.aiff" \
"KaggleBot. Five agents. Three M.C.P. servers. Eleven concepts. 5239 lines of Python. Built with Google A.D.K. and Antigravity IDE. Links in the description. Thanks for watching."

echo "Done! Generated $(ls $OUT_DIR/*.aiff | wc -l) audio segments."
