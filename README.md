

## Orchestration-Free Customer Service Automation: A Privacy-Preserving and Flowchart-Guided Framework


<a href="https://www.python.org/">
<img alt="Python" src="https://img.shields.io/badge/python-%3E=_3.10-blue.svg">
</a>
<a href="https://opensource.org/licenses/MIT">
<img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg">
</a>


---

### Quick Start: Run the Demo System

To experience the flowchart-guided customer service automation demo, follow these simple steps to launch the web-based chatbot system:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Flowchart-Guided-Service-Automation.git
   cd Flowchart-Guided-Service-Automation/demo
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key** (for OpenAI GPT models):
   - Edit `config.py` and set your `OPENAI_API_KEY`.

4. **Launch the web-based demo**:
   ```bash
   ./start.sh
   ```
This will start a local web server (typically at `http://localhost:8000`). Interact with the chatbot to simulate banking scenarios like account inquiries, credit limit adjustments, and travel notifications—all guided by task-oriented flowcharts (TOFs).


### Flowchart Construction and Evaluation

The `flowchart/` directory provides Jupyter notebooks and supporting files for constructing and evaluating Task-Oriented Flowcharts (TOFs) from dialogue data with MultiWOZ and SGD dataset (download the data from [Google Drive](https://drive.google.com/file/d/18ULn5nmzMMM9dMgGvtdybYcKniwdE3dL/view?usp=sharing) and save it in the `flowchart/data` directory).

- **`dialogue_selection.ipynb`**: Implements the Weighted Dialogue Intent Coverage (WDIC) algorithm to select a minimal, representative subset of dialogues that maximizes intent coverage while minimizing computational cost.
- **`flowchart_construction.ipynb`**: Iteratively builds TOFs from selected dialogues using intent extraction, domain detection, and node-type classification.
- **`flowchart_evaluation.ipynb`**: Computes coverage metrics (Utterance Matching Ratio and Complete Path Coverage) by mapping test dialogues to constructed TOFs, assessing semantic alignment and workflow completeness.

The sample flowcharts and evaluation results are presented in **`flowchart/examples`**. 