#!/usr/bin/env python3
"""
compare_versions.py

Comparison script showing the differences between llamaline Ollama and OpenAI versions.
Helps users understand which version is best for their needs.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box

console = Console()

def create_comparison_table():
    """Create a detailed comparison table"""
    table = Table(
        title="🦙 Llamaline: Ollama vs OpenAI Comparison",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("Feature", style="bold cyan", width=20)
    table.add_column("Ollama Version", style="green", width=25)
    table.add_column("OpenAI Version", style="blue", width=25)
    table.add_column("Winner", style="yellow", width=10)
    
    # Add comparison rows
    comparisons = [
        ("Models", "Local (Llama, Gemma, Phi)", "Cloud (GPT-4, GPT-3.5)", "Depends"),
        ("Internet Required", "❌ No", "✅ Yes", "Ollama"),
        ("Setup Complexity", "High (Install Ollama)", "Low (API key only)", "OpenAI"),
        ("Cost", "Free after setup", "Pay per use (~$0.01/task)", "Ollama"),
        ("Privacy", "Fully local", "Data sent to OpenAI", "Ollama"),
        ("AI Quality", "Good", "Excellent", "OpenAI"),
        ("Speed", "Fast (local)", "Fast (cloud)", "Tie"),
        ("Reliability", "Depends on local setup", "High (OpenAI uptime)", "OpenAI"),
        ("Model Variety", "Limited to downloaded", "All OpenAI models", "OpenAI"),
        ("Offline Usage", "✅ Yes", "❌ No", "Ollama"),
        ("Enterprise Ready", "Yes (self-hosted)", "Yes (API limits)", "Tie"),
        ("Learning Curve", "Medium", "Low", "OpenAI")
    ]
    
    for feature, ollama, openai, winner in comparisons:
        table.add_row(feature, ollama, openai, winner)
    
    return table

def create_use_case_panels():
    """Create panels showing ideal use cases for each version"""
    
    ollama_panel = Panel(
        """🏠 **Choose Ollama Version if you:**

• Value complete privacy and data control
• Have good local hardware (8GB+ RAM)
• Work in air-gapped/offline environments
• Want zero ongoing costs
• Need full control over model selection
• Are comfortable with command-line setup
• Work with sensitive/confidential data

💡 **Best for:** Developers, security-conscious users, offline environments""",
        title="🦙 Ollama Version - Local & Private",
        border_style="green",
        width=40
    )
    
    openai_panel = Panel(
        """☁️ **Choose OpenAI Version if you:**

• Want the best AI quality available
• Prefer simple setup (just API key)
• Don't mind cloud-based processing
• Want access to latest models
• Are okay with pay-per-use costs
• Need reliable, always-available service
• Want to get started immediately

💡 **Best for:** Casual users, businesses, quick prototyping""",
        title="🤖 OpenAI Version - Cloud & Powerful", 
        border_style="blue",
        width=40
    )
    
    return Columns([ollama_panel, openai_panel], equal=True)

def create_cost_analysis():
    """Create cost analysis panel"""
    return Panel(
        """💰 **Cost Analysis:**

**Ollama (Local):**
• Initial: $0 (free software)
• Hardware: $500-2000 (good GPU recommended)
• Ongoing: $0 (just electricity)
• Break-even: ~100-1000 tasks

**OpenAI (Cloud):**
• Initial: $0 (no hardware needed)
• Per task: ~$0.005-0.02 (depending on model/length)
• Monthly: $5-50 for typical usage
• Scales with usage""",
        title="💸 Cost Comparison",
        border_style="yellow"
    )

def create_setup_comparison():
    """Create setup steps comparison"""
    
    ollama_setup = Panel(
        """🔧 **Ollama Setup Steps:**

1. Download & install Ollama
2. Pull desired model (2-8GB download)
   `ollama pull gemma3:4b`
3. Ensure sufficient RAM/storage
4. Run llamaline.py
5. Optionally: Configure custom models

⏱️ **Setup time:** 15-30 minutes""",
        title="🦙 Ollama Setup",
        border_style="green",
        width=40
    )
    
    openai_setup = Panel(
        """🔧 **OpenAI Setup Steps:**

1. Get OpenAI API key from platform.openai.com
2. Set environment variable:
   `export OPENAI_API_KEY="your-key"`
3. Install dependencies:
   `pip install openai`
4. Run llamaline_openai.py

⏱️ **Setup time:** 2-5 minutes""",
        title="🤖 OpenAI Setup",
        border_style="blue", 
        width=40
    )
    
    return Columns([ollama_setup, openai_setup], equal=True)

def main():
    """Display comprehensive comparison"""
    console.print()
    console.print("🎯 **Llamaline Version Comparison Guide**", style="bold magenta", justify="center")
    console.print("=" * 60, style="dim")
    console.print()
    
    # Main comparison table
    console.print(create_comparison_table())
    console.print()
    
    # Use case recommendations
    console.print("🎯 **Which Version Should You Choose?**", style="bold cyan")
    console.print()
    console.print(create_use_case_panels())
    console.print()
    
    # Setup comparison
    console.print("⚙️ **Setup Comparison**", style="bold cyan")
    console.print()
    console.print(create_setup_comparison())
    console.print()
    
    # Cost analysis
    console.print(create_cost_analysis())
    console.print()
    
    # Final recommendations
    console.print(Panel(
        """🎯 **Quick Decision Guide:**

• **Just getting started?** → OpenAI version (easier setup)
• **Privacy is critical?** → Ollama version (local processing)
• **Want best AI quality?** → OpenAI version (GPT-4 models)
• **Budget is tight?** → Ollama version (free after setup)
• **Need offline usage?** → Ollama version (works without internet)
• **Want latest features?** → OpenAI version (always updated)

🚀 **Both versions have identical interfaces - easy to switch later!**""",
        title="🎯 Quick Decision Guide",
        border_style="magenta"
    ))
    
    console.print()
    console.print("📁 **File Locations:**", style="bold cyan")
    console.print("• Ollama version: `llamaline/llamaline.py`")
    console.print("• OpenAI version: `llamaline_openai.py`")
    console.print("• Documentation: `README.md` and `README_OPENAI.md`")
    console.print()
    
if __name__ == "__main__":
    main() 