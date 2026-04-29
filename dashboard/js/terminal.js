/**
 * DevOps Agent — Terminal & ReAct Engine Controller
 * Manages agent interactions and step-by-step reasoning visualization.
 */

const terminalOutput = document.getElementById('terminal-output');
const terminalInput = document.getElementById('terminal-input');
const quickBtns = document.querySelectorAll('.quick-btn');

document.addEventListener('DOMContentLoaded', () => {
    initTerminal();
});

function initTerminal() {
    // Handle Input
    terminalInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && terminalInput.value.trim()) {
            const task = terminalInput.value;
            terminalInput.value = '';
            processTask(task);
        }
    });

    // Handle Quick Action Buttons
    quickBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const cmd = btn.getAttribute('data-cmd');
            if (cmd) processTask(cmd);
        });
    });
}

/**
 * Main task processor
 */
async function processTask(task) {
    // 1. Add user message to terminal
    appendLine(`<span class="prompt">agent@nucleus:~$</span> ${task}`);
    
    // 2. Start thinking animation
    const thinkingId = appendLine(`<span class="text-yellow"><i class="fa-solid fa-brain fa-fade"></i> Agent is thinking...</span>`);
    
    try {
        // In a real app, this would be a real API call to your FastAPI backend
        // const response = await fetch('/api/agent/task', { ... });
        // const data = await response.json();
        
        // Simulating ReAct steps for visual premium feel
        await simulateReActFlow(task, thinkingId);
        
    } catch (err) {
        removeLine(thinkingId);
        appendLine(`<span class="react-error"><i class="fa-solid fa-circle-xmark"></i> System Error: ${err.message}</span>`);
    }
}

/**
 * Simulates the ReAct (Reasoning + Acting) loop visually
 */
async function simulateReActFlow(task, thinkingId) {
    await delay(1200);
    removeLine(thinkingId);

    // Step 1: Initial Thought
    await typeLine(`Thought: Analyzing request "${task}". I need to verify the current infrastructure state before proceeding.`, 'react-thought');
    await delay(800);

    // Step 2: Action
    await typeLine(`Action: get_cluster_health`, 'react-action');
    await delay(500);
    await appendLine(`Action Input: {"namespace": "all", "detailed": true}`);
    await delay(1000);

    // Step 3: Observation
    await appendLine(`Observation: 3/3 nodes ready. 12 pods running. No crashes detected. High memory warning on node-03.`, 'react-observation');
    await delay(1200);

    // Step 4: Final Reasoning
    await typeLine(`Thought: Cluster is healthy overall, but node-03 memory pressure requires monitoring. I will provide a summary of all resources.`, 'react-thought');
    await delay(1000);

    // Step 5: Final Answer
    const finalMsg = `Final Answer: Analysis complete. All core services are operational. 
    Memory usage on node-03 is at 71%. I've logged this to the audit trail and established a watch task.`;
    await typeLine(finalMsg, 'react-final');
    
    showToast('Task Completed Successfully', 'success');
}

/**
 * UI Utilities for Terminal
 */
function appendLine(content, className = 'terminal-line') {
    const id = 'line-' + Date.now();
    const line = document.createElement('div');
    line.id = id;
    line.className = className;
    line.innerHTML = content;
    terminalOutput.appendChild(line);
    scrollToBottom();
    return id;
}

function removeLine(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function scrollToBottom() {
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function delay(ms) {
    return new Promise(res => setTimeout(res, ms));
}

async function typeLine(text, className) {
    const id = appendLine('', className);
    const el = document.getElementById(id);
    
    // Typewriter effect
    for (let i = 0; i < text.length; i++) {
        el.innerHTML += text[i];
        if (i % 3 === 0) scrollToBottom(); // Scroll every few chars
        await delay(15);
    }
    return id;
}
