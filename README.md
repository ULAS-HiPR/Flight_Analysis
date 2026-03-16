# Flight Analysis

A tool to graph flight data from the Cats Vega and Eggtimer flight computers.

## Install
1. Clone the repository:
   ```bash
   git clone --recurse-submodules https://github.com/ULAS-HiPR/Flight_Analysis.git
    ```
2. Install dependencies:
    ```bash
    cd Flight_Analysis
    uv sync
    ```

3. Run the tool:
    ```bash
    uv run main.py <arguments>
    ```

## Usage

Run `uv run main.py --help` to see all available options. Example usage:

- Graphing a single flight data file from a Vega flight computer, generating speed and altitude graphs with a custom title:

```bash
uv run main.py --input fl001.cfg VEGA --output-dir graphs --graph-types speed altitude --graph-title "Test Flight"
```

- Graphing a flight with data from both Vega and Eggtimer flight computers, generating all available graph types:

```bash
uv run main.py --input fl001.cfg VEGA --input dtl3.csv EGGTIMER --output-dir graphs --graph-types speed altitude acceleration filtered_altitude --graph-title "Flight Data"    
```
