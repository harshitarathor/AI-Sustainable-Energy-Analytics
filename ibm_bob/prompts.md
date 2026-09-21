# IBM Bob Prompts

All prompts were run in the IBM Bob IDE in **Ask mode** (read-only permissions), after the core project build was complete.

## Prompt 1: Project overview and architecture

- **Mode:** Ask
- **Prompt:** "Read src/, dashboard/, sql/, and notebooks/. Explain how this project works end to end, then give me a Mermaid architecture diagram showing data, notebooks, src modules, the trained model, SQL, and the dashboard pages."
- **Result:** Bob read the project files and explained the full pipeline: raw data, the 6-notebook pipeline, the SQL layer, the src/ library, and the 5-page Streamlit dashboard. It also generated an architecture diagram and listed design observations.
- **How I used it:** Used the explanation to correct my README folder tree (notebook 03 is sql_analysis, dashboard pages have numeric prefixes) and to notice that kpi_queries.sql was a placeholder.
- **Limitations noticed:** The diagram was cluttered and chained the dashboard pages in sequence, implying a flow that doesn't exist.
- **Screenshot:** screenshots/01_overview_architecture.png

## Prompt 2: Simplified architecture

- **Mode:** Ask
- **Prompt:** "Simplify the architecture diagram. Use a clean left-to-right flow with 5 blocks only: Raw Data, Notebook Pipeline (01-06), Processed Artifacts (CSV, DB, model.pkl), src/ Analytics Library (4 modules), and Streamlit Dashboard (5 pages as one block). Remove arrows between individual dashboard pages. Show the SQL layer as a side branch from the processed data. Keep the labels short."
- **Result:** Bob produced a clean left-to-right diagram with the five requested blocks and the SQL layer as a side branch.
- **How I used it:** Final docs/architecture.png, embedded in the README.
- **Screenshot:** screenshots/02_simplified_architecture.png
