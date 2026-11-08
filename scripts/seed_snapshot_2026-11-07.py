import json
N=None
F=["rank","name","url","score","tags","hn_devs","hn_comments_12m","hn_title_points","lobsters","devto","github_stars","downloads_month","tone","note"]
def T(*r): return dict(zip(F,r))
OS,R,FA,NEW="Open source","Rising","Fading","New in 2026"
cats=[]
def C(id,name,tools,also=None,desc=None,verbatim=True):
    cats.append({"id":id,"name":name,"description":desc,"verbatim":verbatim,"tools":tools,"also_scored":also or []})
C("terminal","Terminal agents",[
T(1,"Claude Code","https://code.claude.com",100.0,[],463,32941,78331,6,1913,154893,47376016,0.46,"Default harness in HN setup threads; praised for UX and skills, complaints about usage burn"),
T(2,"Codex CLI","https://developers.openai.com/codex",88.1,[OS,R],277,15265,26411,0,231,133573,95594449,0.27,"Usually the second subscription beside Claude"),
T(3,"OpenCode","https://opencode.ai",84.5,[OS,R],136,5264,6953,2,41,225234,14195259,0.46,"Open harness for any model"),
T(4,"Pi","https://pi.dev",67.5,[OS,R],67,375,166,0,6,120619,1509211,0.73,"Minimal, hackable harness"),
T(5,"DeepSeek Harness","https://deepseek.com/harness/en/",60.1,[OS,NEW],10,499,1265,1,6,275634,N,0.7,"DeepSeek's own desktop and TUI harness"),
T(6,"Aider","https://aider.chat",57.6,[OS,FA],64,324,512,0,2,50007,260509,0.12,"Pre-agent pair programmer"),
T(7,"Gemini CLI","https://github.com/google-gemini/gemini-cli",52.6,[OS],14,1953,4160,0,97,108766,1627950,-0.05,"Called deprecated for subscribers"),
T(8,"Copilot CLI","https://github.com/features/copilot/cli",48.0,[],5,657,316,0,18,11375,6685193,0.44,"Used where work pays for Copilot"),
T(9,"Goose","https://block.github.io/goose",42.7,[OS,R],10,59,485,1,34,56330,N,-0.07,"Block's agent, now under the Linux Foundation"),
T(10,"Mistral Vibe","https://mistral.ai/news/devstral-2-vibe-cli",35.4,[OS],2,83,779,0,1,5331,N,0.43,"Cheap way to run hosted models"),
],["Muse Code","Kimi CLI","Qwen Code","Zerostack","Codewhale","Amp","jcode","Plandex","Droid","Crush","Open Interpreter","Kiro CLI"])
C("editors","Editors & IDEs",[
T(1,"VS Code + Copilot","https://code.visualstudio.com/docs/copilot/overview",87.7,[FA],130,1923,5969,7,183,N,N,0.04,"Work-paid option"),
T(2,"Cursor","https://cursor.com",86.9,[FA],244,7647,25602,3,247,N,N,-0.2,"Usage limits push people to Claude"),
T(3,"Zed","https://zed.dev",83.7,[OS],70,2405,11616,1,8,94166,N,0.31,"Fast Rust editor with ACP agents"),
T(4,"Antigravity","https://antigravity.google",69.0,[],29,1584,5200,0,90,N,N,0.23,"Google's agent IDE and CLI"),
T(5,"Windsurf","https://windsurf.com",64.0,[FA],62,379,5115,0,16,N,N,0.08,"Team now at Google"),
T(6,"Cline","https://cline.bot",63.9,[OS,FA],35,325,879,0,10,71447,N,0.12,"VS Code extension for cheap or local models"),
T(7,"Kiro","https://kiro.dev",56.7,[R],13,433,1797,0,98,N,N,0.16,"Amazon's spec-driven VS Code fork"),
T(8,"Roo Code","https://roocode.com",48.8,[OS],13,72,76,0,2,24240,N,0.46,"Discontinued; forks continue"),
T(9,"Kilo Code","https://kilocode.ai",46.6,[OS],6,69,169,0,0,27898,N,0.4,"Roo Code fork"),
T(10,"Neovim (CodeCompanion / avante)","https://github.com/olimorris/codecompanion.nvim",46.2,[OS],38,12,1,1,13,6927,N,0.44,"AI plugins for Neovim"),
],["JetBrains Junie","Emacs gptel","Continue","Whiteboard","Void"])
C("orchestration","Running many agents",[
T(1,"Herdr","https://herdr.dev",83.6,[OS,NEW],41,552,1346,0,3,49030,N,0.42,"Terminal workspace for many sessions"),
T(2,"tmux + git worktrees","https://git-scm.com/docs/git-worktree",72.9,[R],109,10,0,2,53,N,N,0.42,"DIY baseline, not a product"),
T(3,"Paseo","https://github.com/getpaseo/paseo",65.2,[R],11,175,127,0,1,23394,N,0.43,"Desktop and mobile agent front end"),
T(4,"Gas Town","https://github.com/gastownhall/gastown",61.8,[OS],11,609,1532,0,1,18725,N,-0.52,"Yegge's orchestrator; mostly a punchline"),
T(5,"T3 Code","https://t3.codes",60.5,[OS,NEW],10,64,32,0,3,50869,N,0.65,"GUI for several harnesses"),
T(6,"Beads","https://github.com/steveyegge/beads",60.3,[OS],10,459,338,0,4,28572,N,0.48,"Git-backed issue tracker for agents"),
T(7,"Orca","https://github.com/stablyai/orca",51.2,[OS,NEW],12,9,0,0,2,118432,N,0.52,"Agent IDE for worktrees and remote use"),
T(8,"Conductor","https://conductor.build",49.5,[R],14,42,5,3,2,N,N,0.09,"Mac app, reportedly winding down"),
T(9,"Juggler","https://github.com/juggler-ai/juggler",39.7,[OS,NEW],2,98,330,0,0,853,N,0.27,"GUI agent from JUCE's creator"),
T(10,"Ralph loop","https://ghuntley.com/ralph/",39.2,[],3,51,72,0,8,N,N,0.07,"Prompting pattern, not a product"),
],["Vibe Kanban","Omnara","Munder Difflin","workmux","qm","Ruflo","Superset","Claude Squad","oh-my-claudecode","Sculptor","Crystal","AX (Agent Executor)"])
C("review","Code review & PR agents",[
T(1,"Claude Code review","https://code.claude.com/docs/en/code-review",57.6,[OS,R],13,552,29,0,12,9827,N,-0.31,"Complaints about price per review"),
T(2,"Copilot code review","https://docs.github.com/en/copilot/concepts/agents/code-review",55.1,[],3,75,353,0,1,N,N,-0.13,"Noisy comments; Actions-minutes billing"),
T(3,"CodeRabbit","https://coderabbit.ai",45.9,[],1,149,773,0,3,N,N,-0.08,"The reference-point PR bot"),
T(4,"Cursor Bugbot","https://cursor.com/bugbot",42.4,[],4,25,3,0,2,N,N,0.44,"Most praised bot here"),
T(5,"Codex code review","https://developers.openai.com/codex/integrations/github",39.3,[],1,560,14,0,1,N,N,0.18,"Cross-vendor second opinion"),
T(6,"Codex Security","https://openai.com/index/codex-security/",34.6,[],0,112,662,1,0,N,N,-0.17,"Refusal complaints on defensive work"),
T(7,"Qodo","https://www.qodo.ai",30.1,[OS],0,14,204,0,0,15406,N,-0.33,"Teams often drop it over noise"),
T(8,"Graphite","https://graphite.com",28.8,[],2,359,981,0,2,N,N,0.0,"Stacked PRs; now part of Cursor"),
T(9,"Greptile","https://greptile.com",26.6,[],0,64,90,0,0,N,N,0.25,"Codebase-aware reviewer"),
T(10,"Open Code Review (Alibaba)","https://github.com/alibaba/open-code-review",24.6,[OS,NEW],0,9,0,0,0,49613,N,0.22,"Alibaba's open CLI review tool"),
],["Sourcery","Sphinx"])
C("context","Context, MCP & skills",[
T(1,"AGENTS.md","https://agents.md",94.1,[FA],90,2004,4010,0,161,N,N,0.42,"Default project-rules format"),
T(2,"Agent Skills","https://agentskills.io",81.0,[R],26,1741,233,1,122,N,N,0.24,"Reusable instruction packs"),
T(3,"Superpowers","https://github.com/obra/superpowers",56.5,[OS],10,909,1746,2,15,313991,N,0.2,"Brainstorm-plan-build skills pack"),
T(4,"Spec Kit","https://github.com/github/spec-kit",52.4,[OS],4,138,209,0,6,148358,N,-0.06,"Spec-driven toolkit; document volume complaints"),
T(5,"Context7","https://context7.com",52.3,[OS],6,92,28,0,7,64316,3176334,0.72,"Current library docs via MCP"),
T(6,"GitHub MCP server","https://github.com/github/github-mcp-server",47.4,[OS],3,56,28,0,7,34301,N,0.36,"Official GitHub API MCP server"),
T(7,"Semble","https://github.com/MinishLab/semble",37.4,[OS,NEW],9,58,464,0,15,6377,N,0.33,"Code search claimed cheaper than grep"),
T(8,"rtk","https://github.com/rtk-ai/rtk",36.0,[OS,NEW],0,64,339,0,3,85816,N,-0.08,"Compresses command output; benchmarks disagree"),
T(9,"Impeccable","https://github.com/pbakaus/impeccable",35.9,[OS],1,190,455,0,5,105331,N,0.33,"Design skill; high token use"),
T(10,"Graphify","https://github.com/Graphify-Labs/graphify",31.8,[OS,NEW],0,31,134,0,4,143885,N,0.0,"Codebase knowledge graph"),
],["Figma MCP","Repomix","claude-mem","Linear MCP","Serena","Sentry MCP","codebase-memory-mcp","headroom","context-mode"])
C("browser","Browser & web for agents",[
T(1,"Playwright MCP","https://github.com/microsoft/playwright-mcp",90.8,[OS],13,270,495,1,84,39303,30936316,0.23,"Default agent browser; slow, heavy context"),
T(2,"Chrome DevTools MCP","https://github.com/ChromeDevTools/chrome-devtools-mcp",58.2,[OS],2,44,659,0,15,54930,8604227,0.53,"Real DevTools access"),
T(3,"agent-browser","https://github.com/vercel-labs/agent-browser",48.8,[OS,NEW],1,94,99,0,5,46631,8262982,0.36,"Vercel's browser CLI"),
T(4,"Firecrawl","https://firecrawl.dev",40.5,[OS],0,73,53,0,3,199456,N,0.17,"Scraping API; request-logging criticism"),
T(5,"Lightpanda","https://lightpanda.io",38.7,[OS],0,48,957,0,1,41556,N,-0.25,"Headless browser in Zig"),
T(6,"Stagehand","https://www.stagehand.dev",38.1,[OS],0,44,342,0,1,25978,8473095,0.0,"Browserbase's AI automation framework"),
T(7,"Claude in Chrome","https://claude.com/chrome",35.7,[],0,112,322,0,4,N,N,0.5,"Chrome extension agent"),
T(8,"Vibium","https://github.com/VibiumDev/vibium",35.2,[OS],0,50,448,0,0,2955,N,0.08,"Browser automation from Selenium's creator"),
T(9,"browser-use","https://browser-use.com",29.5,[OS],0,337,413,0,4,120256,8061974,0.0,"Framework for LLM web agents"),
T(10,"Scrapling","https://github.com/D4Vinci/Scrapling",27.0,[OS],0,6,1,0,1,99200,919855,0.67,"Stealthy Python scraping library"),
],["Browser MCP","Jina Reader","Browserbase"])
C("sandbox","Sandboxes & safety",[
T(1,"bubblewrap","https://github.com/containers/bubblewrap",76.7,[OS],7,372,326,0,1,9405,N,0.5,"Linux namespace sandbox"),
T(2,"Docker Sandboxes","https://www.docker.com/products/docker-sandboxes/",76.5,[],6,430,1084,1,2,N,N,0.55,"MicroVM sandboxes; closed source"),
T(3,"OpenShell","https://github.com/NVIDIA/OpenShell",57.5,[OS,NEW],2,64,585,0,2,21245,N,0.0,"NVIDIA policy runtime"),
T(4,"Apple container","https://github.com/apple/container",52.2,[OS],1,195,1275,0,1,51090,N,0.25,"Linux VM containers on macOS"),
T(5,"Dev containers","https://containers.dev",49.8,[],6,27,0,0,4,N,N,0.6,"Guards against agent mistakes, not malice"),
T(6,"E2B","https://e2b.dev",49.6,[OS],1,60,12,0,9,14761,N,0.5,"Hosted Firecracker sandboxes; lock-in"),
T(7,"nono","https://github.com/nolabs-ai/nono",47.7,[OS,NEW],3,9,8,0,2,4886,N,0.33,"Landlock/Seatbelt sandbox, no VM"),
T(8,"smolvm","https://github.com/smol-machines/smolvm",45.4,[OS],1,141,13,0,0,7020,N,0.33,"Cross-platform microVMs"),
T(9,"yoloai","https://github.com/kstenerud/yoloai",39.6,[OS,NEW],2,72,2,0,0,227,N,0.0,"Copy-and-diff sandbox"),
T(10,"Lume","https://github.com/trycua/cua",35.2,[OS],0,16,468,0,1,31942,N,0.0,"macOS/Linux VMs on Apple Silicon"),
],["Daytona","Agent Safehouse","Ardent","Sprites (Fly.io)","container-use","Modal Sandboxes","Vercel Sandbox"])
C("local","Local models & inference",[
T(1,"Ollama","https://ollama.com",100.0,[OS,FA],61,1987,8641,1,126,186256,N,0.6,"Easy local runner; paid cloud tier"),
T(2,"llama.cpp","https://github.com/ggml-org/llama.cpp",88.5,[OS,FA],27,2075,3159,1,29,133652,N,0.39,"C/C++ engine and llama-server"),
T(3,"MLX","https://github.com/ml-explore/mlx",75.2,[OS],10,715,2846,1,8,29089,544885,0.61,"Apple Silicon ML framework"),
T(4,"LM Studio","https://lmstudio.ai",69.5,[FA],18,596,1405,0,11,N,N,0.52,"Desktop GUI for local models"),
T(5,"Open WebUI","https://openwebui.com",69.1,[FA],18,118,261,0,8,158019,N,0.43,"Self-hosted chat UI"),
T(6,"vLLM","https://github.com/vllm-project/vllm",68.4,[OS],5,924,2272,4,36,96519,1857414,0.24,"GPU serving engine"),
T(7,"Unsloth","https://unsloth.ai",57.2,[OS],4,822,1331,0,2,79152,885608,0.2,"Quantized GGUF source"),
T(8,"Lemonade","https://lemonade-server.ai",46.3,[OS],3,35,617,0,4,6140,N,0.5,"AMD local server"),
T(9,"SGLang","https://github.com/sgl-project/sglang",40.8,[OS],1,167,208,0,7,38559,2984581,-0.23,"Datacenter serving framework"),
T(10,"llama-swap","https://github.com/mostlygeek/llama-swap",36.5,[OS],3,53,2,0,0,6205,N,0.53,"Model-swapping proxy"),
],["Apfel","Jan","KoboldCpp"])
C("gateways","Model access & routing",[
T(1,"OpenRouter","https://openrouter.ai",98.5,[R],80,3866,6626,1,18,N,N,0.62,"Pay-as-you-go router"),
T(2,"AWS Bedrock","https://aws.amazon.com/bedrock/",58.4,[],6,461,976,0,116,N,N,0.36,"How companies buy Claude"),
T(3,"LiteLLM","https://github.com/BerriAI/litellm",55.6,[OS],3,431,3453,0,45,62870,92239101,-0.14,"Gateway; PyPI supply-chain talk"),
T(4,"OpenCode Go / Zen","https://opencode.ai/go",54.3,[R],32,35,0,0,1,N,N,0.65,"$10 plan, mostly DeepSeek Flash"),
T(5,"Claude Code Router","https://github.com/musistudio/claude-code-router",35.9,[],N,33,N,N,N,38000,N,N,None),
T(6,"llm (Simon Willison)",None,34,[],9,N,N,N,N,13000,488000,N,None),
T(7,"Vercel AI Gateway",None,28,[],1,25,N,N,N,N,N,N,None),
T(8,"cc-switch",None,25,[],1,N,N,N,N,153000,N,N,None),
T(9,"Portkey",None,21,[],N,N,N,N,N,13000,N,N,None),
T(10,"Chutes",None,20,[],2,32,N,N,N,N,N,N,None),
],["OmniRoute","Cloudflare AI Gateway","Synthetic"])
cats[-1]["verbatim"]="partial (ranks 1-4 verbatim)"
C("frameworks","Build your own agent",[
T(1,"LangChain",None,74,[],4,816,N,N,N,149000,170500000,N,None),
T(2,"Mastra",None,58,[],2,118,N,N,N,29000,10400000,N,None),
T(3,"Claude Agent SDK",None,54,[],2,395,N,N,N,N,58500000,N,None),
T(4,"LangGraph",None,54,[],1,465,N,N,N,45000,44800000,N,None),
T(5,"DSPy",None,53,[],2,130,N,N,N,39000,5300000,N,None),
T(6,"Microsoft Agent Framework",None,50,[],3,N,N,N,N,15000,N,N,None),
T(7,"OpenAI Agents SDK",None,49,[],1,55,N,N,N,31000,12400000,N,None),
T(8,"Google ADK",None,43,[],1,71,N,N,N,22000,10100000,N,None),
T(9,"CrewAI",None,42,[],0,156,N,N,N,61000,2400000,N,None),
T(10,"Pydantic AI",None,41,[],0,110,N,N,N,21000,5400000,N,None),
],[],"SDKs for shipping agents in your product; weakest HN signal, so downloads weigh more.",False)
C("evals","Evals & observability",[
T(1,"OpenTelemetry GenAI",None,55,[],3,49,N,N,N,N,N,N,None),
T(2,"promptfoo",None,48,[],1,48,N,N,N,27000,4000000,N,None),
T(3,"Langfuse",None,46,[],0,125,N,N,N,37000,23600000,N,None),
T(4,"Arize Phoenix",None,42,[FA],30,N,N,N,N,12000,626000,N,None),
T(5,"MLflow",None,38,[],0,55,N,N,N,29000,19900000,N,None),
T(6,"Logfire",None,33,[],0,N,N,N,N,4500,13000000,N,None),
T(7,"Opik",None,29,[],0,N,N,N,N,23000,1700000,N,None),
T(8,"Braintrust",None,29,[],0,32,N,N,N,N,6600000,N,None),
T(9,"Helicone",None,28,[],0,N,N,N,N,6300,N,N,None),
T(10,"DeepEval",None,28,[],0,N,N,N,N,19000,2600000,N,None),
],["LangSmith","Inspect AI","garak","Weights & Biases Weave","Laminar"],"Traces, evals and regression tests; thin on HN, a shortlist rather than a verdict.",False)
C("assistants","Always-on agents",[
T(1,"OpenClaw",None,93,[R],72,5100,N,N,N,394000,N,N,None),
T(2,"Hermes Agent",None,82,[R],54,507,N,N,N,261000,N,N,None),
T(3,"Muse",None,67,[R],21,86,N,N,N,N,N,N,None),
T(4,"Claude Cowork",None,60,[],40,937,N,N,N,N,N,N,None),
T(5,"n8n",None,60,[],4,429,N,N,N,210000,N,N,None),
T(6,"NanoClaw",None,48,[NEW],3,200,N,N,N,31000,N,N,None),
T(7,"Home Assistant + LLM",None,47,[R],13,93,N,N,N,N,N,N,None),
T(8,"Claude Duet",None,37,[],3,32,N,N,N,N,N,N,None),
T(9,"Dots",None,22,[],1,24,N,N,N,N,N,N,None),
T(10,"Paperclip",None,20,[NEW],0,N,N,N,N,112000,N,N,None),
],["Claude Code Routines","nanobot","Eigent"],"Personal agents on a server or Mac mini that run while you are away.",False)
for c in cats:
    for t in c["tools"]:
        t["tags"]=t["tags"]
snap={"schema_version":1,"snapshot_date":"2026-11-07","edition":"November 2026",
 "source":{"name":"AI Dev Tools Field Guide","author":"Alexis Santos","url":"https://alexissantos.dev/ai-dev-tools/","data_url":"https://alexissantos.dev/ai-dev-tools/tools.json","retrieved_at":"2026-11-08"},
 "corpus":{"hn_comments":6323,"ask_hn_threads":24,"hn_stories":3229,"lobsters_stories":2979,"devto_posts":42357,"tools_scored":191},
 "fields":{"score":"Alexis's composite score, 0-100, normalised to the category leader","hn_devs":"HN developers naming the tool in Ask HN setup threads (May 2025 - Nov 2026)","hn_comments_12m":"HN comments mentioning the tool, last 12 months","hn_title_points":"HN front-page points on stories about the tool","lobsters":"Lobsters stories","devto":"dev.to posts","github_stars":"GitHub stars","downloads_month":"npm/PyPI downloads last month","tone":"HN sentiment, -1 to 1","tags":"Rising, Fading, New in 2026, Open source"},
 "notes":"Categories marked verbatim=false (and gateways ranks 5-10) were transcribed from the rendered page, not the JSON; numbers are rounded (e.g. stars 38k) and URLs missing. Re-fetch tools.json to fill gaps.",
 "polls":[{"id":"hn-agentic-setup-2026-11","title":"Ask HN: What's your current AI agentic setup?","url":"https://news.ycombinator.com/item?id=50366117","respondents":538,
   "results":[["Claude Code",140],["Codex CLI",128],["OpenCode",89],["Their own harness",58],["Pi",45],["Cursor",25],["VS Code/Copilot",24],["Zed",15],["Antigravity",9],["DeepSeek Harness",9],["Kiro",7],["Aider",5]]}],
 "categories":cats}
snap["polls"][0]["results"]=[{"name":a,"count":b} for a,b in snap["polls"][0]["results"]]
import sys
out=sys.argv[1]
json.dump(snap,open(out+"/2026-11-07.json","w"),indent=1,ensure_ascii=False)
json.dump({"snapshots":["2026-11-07"],"latest":"2026-11-07"},open(out+"/index.json","w"),indent=1)
print("ok",sum(len(c["tools"]) for c in cats))
