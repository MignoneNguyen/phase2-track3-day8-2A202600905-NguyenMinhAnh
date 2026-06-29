import json
import markdown
import os

def generate_report():
    # 1. Read JSON metrics
    with open(r'd:\VinAI\phase2-track3-day8-langgraph-agent\outputs\metrics.json', 'r') as f:
        metrics_data = json.load(f)
        
    # 2. Read Markdown report
    with open(r'd:\VinAI\phase2-track3-day8-langgraph-agent\reports\lab_report.md', 'r') as f:
        md_content = f.read()
        
    # Convert MD to HTML with table extension
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # 3. Read Mermaid diagram
    mermaid_code = ""
    mermaid_path = r'd:\VinAI\phase2-track3-day8-langgraph-agent\outputs\graph_diagram.md'
    if os.path.exists(mermaid_path):
        with open(mermaid_path, 'r') as f:
            content = f.read()
            if '```mermaid' in content:
                mermaid_code = content.split('```mermaid')[1].split('```')[0].strip()
                
    # Extract paths for scenarios
    scenario_paths = {s['scenario_id']: s.get('path', []) for s in metrics_data.get('scenario_metrics', [])}
    
    # Generate buttons
    buttons_html = '<button class="scenario-btn active" onclick="renderScenario(\'all\', event)">Default View</button>\n'
    for s_id in scenario_paths.keys():
        buttons_html += f'<button class="scenario-btn" onclick="renderScenario(\'{s_id}\', event)">{s_id}</button>\n'
            
    # 4. Generate HTML template
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangGraph Agent Lab Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0f172a;
            --text-color: #f8fafc;
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.1);
            --accent-color: #60a5fa;
            --accent-hover: #93c5fd;
            --success: #34d399;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Outfit', sans-serif;
        }}
        
        body {{
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            color: var(--text-color);
            min-height: 100vh;
            padding: 3rem 1rem;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 3rem;
            animation: fadeInDown 0.8s ease;
        }}
        
        h1 {{
            font-size: 3rem;
            background: linear-gradient(to right, #93c5fd, #c4b5fd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        
        .glass-card {{
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: fadeInUp 0.8s ease forwards;
            opacity: 0;
        }}
        
        .glass-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.6);
        }}
        
        /* Staggered animation for cards */
        .glass-card:nth-child(1) {{ animation-delay: 0.1s; }}
        .glass-card:nth-child(2) {{ animation-delay: 0.2s; }}
        .glass-card:nth-child(3) {{ animation-delay: 0.3s; }}
        .glass-card:nth-child(4) {{ animation-delay: 0.4s; }}
        
        h2 {{
            color: var(--accent-hover);
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-size: 1.8rem;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 0.5rem;
        }}
        
        ul, ol {{
            margin-left: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        li {{
            margin-bottom: 0.5rem;
        }}
        
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 1.5rem 0;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--card-border);
            background: rgba(15, 23, 42, 0.4);
        }}
        
        th, td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--card-border);
        }}
        
        th {{
            background: rgba(255, 255, 255, 0.08);
            font-weight: 700;
            color: #bfdbfe;
            text-transform: uppercase;
            font-size: 0.9rem;
            letter-spacing: 0.5px;
        }}
        
        td {{
            color: #e2e8f0;
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        tr:hover td {{
            background: rgba(255, 255, 255, 0.05);
        }}
        
        strong {{
            color: #fff;
            font-weight: 700;
        }}
        
        .diagram-container {{
            text-align: center;
            margin: 1rem 0 2rem 0;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            border: 1px solid var(--card-border);
            overflow: auto;
        }}
        
        .mermaid {{
            display: flex;
            justify-content: center;
        }}
        
        .diagram-container:hover {{
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) inset;
        }}
        
        /* Stats row */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .stat-box {{
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .stat-box:hover {{
            background: rgba(59, 130, 246, 0.2);
            transform: translateY(-3px);
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--success);
            margin-bottom: 0.5rem;
            text-shadow: 0 0 10px rgba(52, 211, 153, 0.4);
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #94a3b8;
            font-weight: 600;
        }}
        
        .scenario-btn {{
            background: rgba(59, 130, 246, 0.2);
            color: #bfdbfe;
            border: 1px solid rgba(59, 130, 246, 0.4);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: 600;
        }}
        
        .scenario-btn:hover {{
            background: rgba(59, 130, 246, 0.4);
        }}
        
        .scenario-btn.active {{
            background: #3b82f6;
            color: white;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
            border-color: #60a5fa;
        }}
        
        @keyframes fadeInDown {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .code-block {{
            background: #0f172a;
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid var(--card-border);
            font-family: monospace;
            font-size: 0.9rem;
            color: #a5b4fc;
        }}
        
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Agent Lab Report</h1>
            <p>LangGraph Orchestration & Metrics Analysis</p>
        </header>

        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-value">{metrics_data.get('success_rate', 0) * 100}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{metrics_data.get('total_scenarios', 0)}</div>
                <div class="stat-label">Total Scenarios</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{metrics_data.get('total_interrupts', 0)}</div>
                <div class="stat-label">HITL Interrupts</div>
            </div>
        </div>
        
        <div class="glass-card">
            <h2>Interactive Graph Architecture</h2>
            <p style="margin-bottom: 1rem; color: #cbd5e1;">Select a scenario to visualize its execution path through the graph.</p>
            <div style="margin-bottom: 1rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
                {buttons_html}
            </div>
            <div class="diagram-container">
                <div class="mermaid" id="mermaid-view">
                    {mermaid_code}
                </div>
            </div>
        </div>

        <div class="glass-card markdown-content">
            {html_content}
        </div>
        
        <div class="glass-card">
            <h2>Raw JSON Metrics</h2>
            <div class="code-block">
                <pre>{json.dumps(metrics_data, indent=2)}</pre>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ 
            startOnLoad: true, 
            theme: 'dark',
            securityLevel: 'loose'
        }});
        
        const rawMermaid = `{mermaid_code.replace("`", "\\`")}`;
        const scenarioPaths = {json.dumps(scenario_paths)};
        
        async function renderScenario(scenarioId, event) {{
            // update active button
            if (event) {{
                document.querySelectorAll('.scenario-btn').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
            }}
            
            let mermaidCode = rawMermaid;
            if (scenarioId !== 'all') {{
                const path = scenarioPaths[scenarioId];
                if (path) {{
                    const uniqueNodes = [...new Set(path)];
                    uniqueNodes.forEach(node => {{
                        if (node !== 'unknown') {{
                            mermaidCode += `\\nstyle ${{node}} fill:#3b82f6,stroke:#fff,stroke-width:2px,color:#fff`;
                        }}
                    }});
                }}
            }}
            
            // Render dynamically
            const graphDiv = document.getElementById('mermaid-view');
            graphDiv.innerHTML = '';
            
            try {{
                const {{ svg }} = await mermaid.render('mermaid-dynamic-svg', mermaidCode);
                graphDiv.innerHTML = svg;
            }} catch (e) {{
                console.error("Mermaid render error:", e);
                graphDiv.innerHTML = `<div class="mermaid">${{mermaidCode}}</div>`;
                mermaid.init(undefined, graphDiv.querySelectorAll('.mermaid'));
            }}
        }}
    </script>
</body>
</html>
"""
    
    # Write the output file
    output_path = r'd:\VinAI\phase2-track3-day8-langgraph-agent\outputs\report.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"HTML report successfully generated at: {{output_path}}")

if __name__ == '__main__':
    generate_report()
