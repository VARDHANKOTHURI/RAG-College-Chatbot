// College RAG Chatbot Single Page Application
const API_BASE = '/api';

// State Store
const state = {
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token') || null,
  currentView: 'home',
  conversations: [],
  currentConversationId: null,
  messages: [],
  documents: [],
  analytics: null,
  unansweredQuestions: [],
  feedbackList: [],
  isStreaming: false,
  selectedLanguage: 'English',
  selectedDepartment: 'All',
  theme: localStorage.getItem('theme') || 'dark',
};

// Utilities
function setToken(token, user) {
  state.token = token;
  state.user = user;
  if (token) {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
  } else {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
  renderNav();
}

async function request(endpoint, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (state.token) {
    headers['Authorization'] = `Bearer ${state.token}`;
  }
  const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
  if (res.status === 401 && !endpoint.includes('/auth/login')) {
    setToken(null, null);
    navigate('login');
    throw new Error('Unauthorized');
  }
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(errorData.message || errorData.detail?.message || 'Request failed');
  }
  return res.json();
}

// Router
function navigate(view, params = {}) {
  state.currentView = view;
  window.history.pushState({}, '', `/${view === 'home' ? '' : view}`);
  render();

  if (view === 'chat') {
    loadConversationsList();
    if (params.conversationId) {
      loadConversation(params.conversationId);
    }
  } else if (view === 'documents') {
    loadDocumentsList();
  } else if (view === 'admin') {
    loadAdminData();
  }
}

window.addEventListener('popstate', () => {
  const path = window.location.pathname.replace('/', '') || 'home';
  navigate(path);
});

// Markdown Formatter (Lightweight safe parser)
function parseMarkdown(text) {
  if (!text) return '';
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/### (.*?)\n/g, '<h4 class="text-base font-bold mt-3 mb-1 text-indigo-300">$1</h4>')
    .replace(/## (.*?)\n/g, '<h3 class="text-lg font-bold mt-4 mb-2 text-indigo-400">$1</h3>')
    .replace(/# (.*?)\n/g, '<h2 class="text-xl font-extrabold mt-4 mb-2 text-indigo-400">$1</h2>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-indigo-200 font-semibold">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code class="bg-gray-800 text-cyan-300 px-1.5 py-0.5 rounded text-xs">$1</code>')
    .replace(/^\- (.*?)$/gm, '<li class="ml-4 list-disc">$1</li>')
    .replace(/^\d+\. (.*?)$/gm, '<li class="ml-4 list-decimal">$1</li>')
    .replace(/\n\n/g, '<p class="mb-2.5"></p>')
    .replace(/\n/g, '<br/>');
  return html;
}

// Navigation Renderer
function renderNav() {
  const navContainer = document.getElementById('navbar');
  if (!navContainer) return;

  const isAdmin = state.user?.role === 'admin';
  const isLoggedIn = !!state.token;

  navContainer.innerHTML = `
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3 cursor-pointer" onclick="navigate('home')">
        <div class="w-10 h-10 rounded-xl glow-gradient flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
        </div>
        <div>
          <span class="text-lg font-bold gradient-text tracking-tight block leading-tight">CampusAI</span>
          <span class="text-[10px] text-gray-400 font-mono tracking-widest uppercase">RAG College Assistant</span>
        </div>
      </div>

      <div class="flex items-center gap-2 sm:gap-4">
        ${isLoggedIn ? `
          <button onclick="navigate('chat')" class="px-3 py-1.5 rounded-lg text-sm font-medium ${state.currentView === 'chat' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:text-white hover:bg-gray-800'} transition flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
            <span>Chat</span>
          </button>

          <button onclick="navigate('documents')" class="px-3 py-1.5 rounded-lg text-sm font-medium ${state.currentView === 'documents' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:text-white hover:bg-gray-800'} transition flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            <span>Knowledge Base</span>
          </button>

          ${isAdmin ? `
            <button onclick="navigate('admin')" class="px-3 py-1.5 rounded-lg text-sm font-medium ${state.currentView === 'admin' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:text-white hover:bg-gray-800'} transition flex items-center gap-1.5">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
              <span>Admin Panel</span>
            </button>
          ` : ''}

          <button onclick="navigate('settings')" class="px-3 py-1.5 rounded-lg text-sm font-medium ${state.currentView === 'settings' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:text-white hover:bg-gray-800'} transition flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
            <span class="hidden sm:inline">${state.user?.name?.split(' ')[0] || 'Profile'}</span>
          </button>

          <button onclick="handleLogout()" class="text-gray-400 hover:text-red-400 p-1.5 rounded-lg hover:bg-gray-800 transition" title="Logout">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
          </button>
        ` : `
          <button onclick="navigate('login')" class="btn-secondary text-sm py-1.5 px-4">Sign In</button>
          <button onclick="navigate('register')" class="btn-primary text-sm py-1.5 px-4">Register</button>
        `}
      </div>
    </div>
  `;
}

// ----------------------------------------------------
// Page Views
// ----------------------------------------------------

// 1. Landing / Home Page
function renderHome() {
  return `
    <div class="animate-fade-in max-w-6xl mx-auto px-4 py-12">
      <!-- Hero Section -->
      <div class="text-center space-y-6 max-w-3xl mx-auto pt-6">
        <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass-panel text-xs font-semibold text-indigo-400 border-indigo-500/30">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          Autonomous RAG Knowledge Engine Active
        </div>
        <h1 class="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight">
          Instant, Grounded Answers for <span class="gradient-text">College Students</span>
        </h1>
        <p class="text-lg text-gray-400">
          Ask questions about admissions, semester exams, fee structures, hostel policies, and campus life with verified source citations from authorized college documents.
        </p>

        <div class="flex flex-wrap items-center justify-center gap-4 pt-4">
          <button onclick="navigate('chat')" class="btn-primary text-base px-6 py-3">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
            <span>Start Chatting Now</span>
          </button>
          <button onclick="navigate('documents')" class="btn-secondary text-base px-6 py-3">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
            <span>Explore Knowledge Base</span>
          </button>
        </div>
      </div>

      <!-- Demo Accounts Card -->
      <div class="mt-16 glass-panel p-6 max-w-2xl mx-auto border-indigo-500/20">
        <h3 class="text-sm font-semibold uppercase tracking-wider text-indigo-400 mb-3 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          Quick Demo Accounts (1-Click Sign In)
        </h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div onclick="quickLogin('student@college.edu', 'Student@123')" class="p-3 rounded-xl bg-gray-800/60 border border-gray-700/50 hover:border-indigo-500 cursor-pointer transition flex items-center justify-between">
            <div>
              <div class="font-semibold text-white text-sm">Demo Student</div>
              <div class="text-xs text-gray-400">student@college.edu</div>
            </div>
            <span class="badge badge-score">Student</span>
          </div>
          <div onclick="quickLogin('admin@college.edu', 'Admin@123')" class="p-3 rounded-xl bg-gray-800/60 border border-gray-700/50 hover:border-indigo-500 cursor-pointer transition flex items-center justify-between">
            <div>
              <div class="font-semibold text-white text-sm">Admin Portal</div>
              <div class="text-xs text-gray-400">admin@college.edu</div>
            </div>
            <span class="badge badge-ready">Admin</span>
          </div>
        </div>
      </div>

      <!-- Feature Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
        <div class="glass-panel p-6 hover:border-indigo-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
          </div>
          <h3 class="text-lg font-bold text-white mb-2">Zero-Hallucination Grounding</h3>
          <p class="text-sm text-gray-400">Answers strictly synthesized from verified college handbooks with direct source citations.</p>
        </div>

        <div class="glass-panel p-6 hover:border-indigo-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-4">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          </div>
          <h3 class="text-lg font-bold text-white mb-2">Hybrid Semantic Retrieval</h3>
          <p class="text-sm text-gray-400">Combines Qdrant dense vector similarity with keyword ranking for course codes, dates, and fee items.</p>
        </div>

        <div class="glass-panel p-6 hover:border-indigo-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-4">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
          </div>
          <h3 class="text-lg font-bold text-white mb-2">Knowledge Gap Analytics</h3>
          <p class="text-sm text-gray-400">Unanswered questions are logged automatically to help administrators update guidelines.</p>
        </div>
      </div>
    </div>
  `;
}

// 2. Chat Page
function renderChat() {
  const suggestedQuestions = [
    "What is the annual hostel fee for a 2-sharing AC room?",
    "When are the Odd Semester End examinations in 2026?",
    "What is the minimum attendance percentage required for exams?",
    "What scholarships are offered for meritorious students?",
    "What was the highest international placement package offered?",
    "What is the fee for examination revaluation per paper?"
  ];

  return `
    <div class="flex h-[calc(100vh-4rem)] overflow-hidden">
      <!-- Sidebar / Conversation History -->
      <aside class="w-72 bg-gray-900/90 border-r border-gray-800 flex flex-col hidden md:flex">
        <div class="p-4 border-b border-gray-800 flex items-center justify-between">
          <button onclick="createNewChat()" class="btn-primary w-full text-sm py-2 justify-center">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            <span>New Chat</span>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-3 space-y-1" id="conversationList">
          ${renderConversationItems()}
        </div>

        <!-- Language & Filter Settings -->
        <div class="p-3 border-t border-gray-800 bg-gray-950/60 space-y-2 text-xs">
          <div class="flex items-center justify-between text-gray-400">
            <span>Response Language:</span>
            <select id="langSelect" onchange="state.selectedLanguage = this.value" class="bg-gray-800 text-white rounded px-2 py-1 border border-gray-700 outline-none">
              <option value="English" ${state.selectedLanguage === 'English' ? 'selected' : ''}>English</option>
              <option value="Hindi" ${state.selectedLanguage === 'Hindi' ? 'selected' : ''}>Hindi (हिंदी)</option>
              <option value="Telugu" ${state.selectedLanguage === 'Telugu' ? 'selected' : ''}>Telugu (తెలుగు)</option>
            </select>
          </div>
        </div>
      </aside>

      <!-- Main Chat Area -->
      <main class="flex-1 flex flex-col bg-gray-950 relative">
        <!-- Messages Scroll Container -->
        <div id="messagesContainer" class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 max-w-4xl w-full mx-auto">
          ${state.messages.length === 0 ? `
            <div class="text-center py-12 space-y-6">
              <div class="w-16 h-16 rounded-2xl glow-gradient mx-auto flex items-center justify-center shadow-xl shadow-indigo-500/20">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
              </div>
              <div class="max-w-md mx-auto">
                <h2 class="text-2xl font-bold text-white mb-2">How can I assist you today?</h2>
                <p class="text-sm text-gray-400">Ask about courses, academic rules, fees, hostel, scholarships, placements or exams.</p>
              </div>

              <!-- Suggested Questions -->
              <div class="pt-4 max-w-2xl mx-auto">
                <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Suggested Inquiries</div>
                <div class="flex flex-wrap justify-center gap-2">
                  ${suggestedQuestions.map(q => `
                    <button onclick="askPresetQuestion('${q.replace(/'/g, "\\'")}')" class="text-xs bg-gray-900 border border-gray-800 hover:border-indigo-500/50 hover:bg-gray-800 text-gray-300 py-2 px-3 rounded-xl transition text-left">
                      ${q}
                    </button>
                  `).join('')}
                </div>
              </div>
            </div>
          ` : `
            ${state.messages.map(m => renderMessageItem(m)).join('')}
          `}
          ${state.isStreaming ? `
            <div class="flex items-start gap-3 message-assistant message-bubble animate-fade-in">
              <div class="w-7 h-7 rounded-lg glow-gradient flex-shrink-0 flex items-center justify-center text-xs text-white font-bold">AI</div>
              <div class="space-y-2 flex-1">
                <div id="streamingText" class="text-sm text-gray-200">Generating grounded response...</div>
              </div>
            </div>
          ` : ''}
        </div>

        <!-- Chat Input Bar -->
        <div class="p-4 border-t border-gray-800 bg-gray-900/60 backdrop-blur-lg">
          <form onsubmit="handleSendMessage(event)" class="max-w-4xl mx-auto flex items-center gap-3">
            <div class="flex-1 relative">
              <input
                id="chatInput"
                type="text"
                placeholder="Ask a question about Greenwood College..."
                class="w-full bg-gray-950 border border-gray-800 focus:border-indigo-500 text-white rounded-xl pl-4 pr-10 py-3 text-sm outline-none transition shadow-inner"
                autocomplete="off"
                required
              />
            </div>
            <button type="submit" id="sendBtn" class="btn-primary py-3 px-5 rounded-xl flex-shrink-0">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
            </button>
          </form>
        </div>
      </main>
    </div>
  `;
}

function renderConversationItems() {
  if (state.conversations.length === 0) {
    return `<div class="text-xs text-gray-500 text-center py-4">No conversations yet</div>`;
  }
  return state.conversations.map(c => `
    <div class="group flex items-center justify-between p-2.5 rounded-lg cursor-pointer ${state.currentConversationId === c.id ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30' : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'} transition" onclick="loadConversation('${c.id}')">
      <div class="flex items-center gap-2 truncate text-xs font-medium">
        <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
        <span class="truncate">${c.title || 'Conversation'}</span>
      </div>
      <button onclick="event.stopPropagation(); handleDeleteConversation('${c.id}')" class="opacity-0 group-hover:opacity-100 hover:text-red-400 p-1 transition" title="Delete">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
      </button>
    </div>
  `).join('');
}

function renderMessageItem(m) {
  const isUser = m.role === 'user';
  if (isUser) {
    return `
      <div class="flex justify-end animate-fade-in">
        <div class="message-bubble message-user text-sm">${m.content}</div>
      </div>
    `;
  }

  const sources = m.sources || [];
  return `
    <div class="flex items-start gap-3 message-assistant message-bubble animate-fade-in">
      <div class="w-7 h-7 rounded-lg glow-gradient flex-shrink-0 flex items-center justify-center text-xs text-white font-bold shadow-md shadow-indigo-500/20">AI</div>
      <div class="space-y-3 flex-1 overflow-hidden">
        <div class="text-sm text-gray-200 leading-relaxed">${parseMarkdown(m.content)}</div>

        ${sources.length > 0 ? `
          <div class="pt-2 border-t border-gray-800/80">
            <div class="text-xs font-semibold text-indigo-400 mb-2 flex items-center gap-1.5">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              <span>Verified Source Documents (${sources.length})</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              ${sources.map((s, idx) => `
                <div class="source-card text-xs">
                  <div class="flex items-center justify-between gap-1 mb-1">
                    <span class="font-semibold text-white truncate" title="${s.title}">${s.title}</span>
                    <span class="badge badge-score flex-shrink-0">Page ${s.pageNumber || 1}</span>
                  </div>
                  <div class="text-gray-400 line-clamp-2 text-[11px] mb-1.5">${s.snippet}</div>
                  <div class="flex items-center justify-between text-[10px] text-gray-500">
                    <span>${s.category || 'General'}</span>
                    <span>Relevance: ${Math.round((s.score || 0.5) * 100)}%</span>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}

        <!-- Feedback Actions -->
        <div class="flex items-center justify-between pt-1 text-xs text-gray-500">
          <div class="flex items-center gap-2">
            <span>Was this answer helpful?</span>
            <button onclick="handleFeedback('${m.id}', 1)" class="hover:text-emerald-400 p-1 rounded transition" title="Helpful">👍</button>
            <button onclick="openFeedbackModal('${m.id}')" class="hover:text-rose-400 p-1 rounded transition" title="Not helpful">👎</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

// 3. Document Management Page
function renderDocuments() {
  const isAdmin = state.user?.role === 'admin';
  return `
    <div class="animate-fade-in max-w-6xl mx-auto px-4 py-8 space-y-8">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl sm:text-3xl font-extrabold text-white">Authorized College Knowledge Base</h1>
          <p class="text-sm text-gray-400">All student responses are grounded in these ingested documents.</p>
        </div>
        ${isAdmin ? `
          <button onclick="openUploadModal()" class="btn-primary self-start text-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            <span>Upload New Document</span>
          </button>
        ` : ''}
      </div>

      <!-- Document Table -->
      <div class="glass-panel overflow-hidden">
        <div class="overflow-x-auto">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Document Title</th>
                <th>Category</th>
                <th>Academic Year</th>
                <th>Pages</th>
                <th>Chunks</th>
                <th>Status</th>
                ${isAdmin ? `<th>Actions</th>` : ''}
              </tr>
            </thead>
            <tbody id="documentTableBody">
              ${renderDocumentRows()}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}

function renderDocumentRows() {
  const isAdmin = state.user?.role === 'admin';
  if (state.documents.length === 0) {
    return `<tr><td colspan="${isAdmin ? 7 : 6}" class="text-center py-8 text-gray-500">No documents in knowledge base</td></tr>`;
  }
  return state.documents.map(d => `
    <tr>
      <td>
        <div class="font-semibold text-white">${d.title}</div>
        <div class="text-xs text-gray-400 font-mono">${d.fileName}</div>
      </td>
      <td><span class="badge bg-gray-800 text-gray-300 border border-gray-700">${d.category}</span></td>
      <td class="text-xs text-gray-300">${d.academicYear || '2026'} (v${d.version || 1})</td>
      <td class="text-xs text-gray-300">${d.totalPages}</td>
      <td class="text-xs text-indigo-300 font-mono font-semibold">${d.totalChunks}</td>
      <td>
        <span class="badge ${d.status === 'ready' ? 'badge-ready' : d.status === 'processing' ? 'badge-processing' : 'badge-failed'}">
          ${d.status.toUpperCase()}
        </span>
      </td>
      ${isAdmin ? `
        <td>
          <div class="flex items-center gap-2">
            <button onclick="handleReprocessDoc('${d.id}')" class="p-1.5 text-gray-400 hover:text-indigo-400 hover:bg-gray-800 rounded transition" title="Reprocess Vectors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
            </button>
            <button onclick="handleDeleteDoc('${d.id}')" class="p-1.5 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded transition" title="Delete Document">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
            </button>
          </div>
        </td>
      ` : ''}
    </tr>
  `).join('');
}

// 4. Admin Analytics Page
function renderAdmin() {
  const m = state.analytics || {
    totalDocuments: 0,
    totalChunks: 0,
    totalQuestions: 0,
    answeredQuestions: 0,
    unansweredQuestions: 0,
    activeUsers: 0,
    positiveFeedbackCount: 0,
    negativeFeedbackCount: 0,
    popularQuestions: []
  };

  return `
    <div class="animate-fade-in max-w-6xl mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-white">Administrator Analytics & Control</h1>
        <p class="text-sm text-gray-400">Knowledge base metrics, student query patterns, and unanswered question gaps.</p>
      </div>

      <!-- KPI Metrics -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4" id="adminKpis">
        <div class="glass-panel p-5">
          <div class="text-xs text-gray-400 font-medium uppercase tracking-wider mb-1">Knowledge Docs</div>
          <div class="text-3xl font-extrabold text-white">${m.totalDocuments}</div>
          <div class="text-xs text-indigo-400 mt-1">${m.totalChunks} searchable chunks</div>
        </div>
        <div class="glass-panel p-5">
          <div class="text-xs text-gray-400 font-medium uppercase tracking-wider mb-1">Total Queries</div>
          <div class="text-3xl font-extrabold text-white">${m.totalQuestions}</div>
          <div class="text-xs text-emerald-400 mt-1">${m.answeredQuestions} grounded answers</div>
        </div>
        <div class="glass-panel p-5">
          <div class="text-xs text-gray-400 font-medium uppercase tracking-wider mb-1">Knowledge Gaps</div>
          <div class="text-3xl font-extrabold text-amber-400">${m.unansweredQuestions}</div>
          <div class="text-xs text-gray-500 mt-1">Needs document upload</div>
        </div>
        <div class="glass-panel p-5">
          <div class="text-xs text-gray-400 font-medium uppercase tracking-wider mb-1">Feedback Ratio</div>
          <div class="text-3xl font-extrabold text-cyan-400">${m.positiveFeedbackCount} 👍 / ${m.negativeFeedbackCount} 👎</div>
          <div class="text-xs text-gray-500 mt-1">${m.activeUsers} registered users</div>
        </div>
      </div>

      <!-- Popular Inquiries & Unanswered Questions -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Popular Inquiries -->
        <div class="glass-panel p-6">
          <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
            <span>Frequently Asked Student Inquiries</span>
          </h3>
          <div class="space-y-3" id="adminPopularList">
            ${(m.popularQuestions || []).map(p => `
              <div class="flex items-center justify-between p-3 rounded-xl bg-gray-900/60 border border-gray-800">
                <span class="text-sm text-gray-200">${p.question}</span>
                <span class="badge badge-score">${p.count} asks</span>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Unanswered Questions / Knowledge Gaps -->
        <div class="glass-panel p-6">
          <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
            <span>Unanswered Inquiries (Knowledge Gaps)</span>
          </h3>
          <div class="space-y-3 max-h-80 overflow-y-auto" id="adminUnansweredList">
            ${state.unansweredQuestions.length === 0 ? `
              <div class="text-center py-8 text-gray-500 text-sm">No unresolved student questions!</div>
            ` : state.unansweredQuestions.map(u => `
              <div class="p-3 rounded-xl bg-gray-900/60 border border-gray-800 flex items-start justify-between gap-3">
                <div>
                  <div class="text-sm font-semibold text-white">${u.question}</div>
                  <div class="text-xs text-gray-500 mt-1">Status: ${u.status}</div>
                </div>
                <button onclick="handleResolveUnanswered('${u.id}')" class="text-xs bg-emerald-600/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-600 hover:text-white px-2.5 py-1 rounded transition">
                  Resolve
                </button>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    </div>
  `;
}

// 5. Settings / Profile Page
function renderSettings() {
  return `
    <div class="animate-fade-in max-w-2xl mx-auto px-4 py-8 space-y-6">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-white">Account & System Settings</h1>

      <div class="glass-panel p-6 space-y-4">
        <h3 class="text-lg font-bold text-white mb-2">User Profile</h3>
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 rounded-2xl glow-gradient flex items-center justify-center text-xl font-bold text-white">
            ${state.user?.name?.charAt(0) || 'U'}
          </div>
          <div>
            <div class="text-lg font-bold text-white">${state.user?.name || 'Guest'}</div>
            <div class="text-sm text-gray-400">${state.user?.email || 'Not logged in'}</div>
            <span class="badge ${state.user?.role === 'admin' ? 'badge-ready' : 'badge-score'} mt-1">
              ${(state.user?.role || 'student').toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      <div class="glass-panel p-6 space-y-4">
        <h3 class="text-lg font-bold text-white">System Diagnostics</h3>
        <div class="space-y-2 text-sm text-gray-300">
          <div class="flex justify-between py-1 border-b border-gray-800">
            <span class="text-gray-400">RAG Framework:</span>
            <span class="font-mono text-cyan-300">LangChain + FastAPI</span>
          </div>
          <div class="flex justify-between py-1 border-b border-gray-800">
            <span class="text-gray-400">Vector Engine:</span>
            <span class="font-mono text-cyan-300">Qdrant Vector Database</span>
          </div>
          <div class="flex justify-between py-1 border-b border-gray-800">
            <span class="text-gray-400">Database Layer:</span>
            <span class="font-mono text-cyan-300">MongoDB with Async Fallback</span>
          </div>
          <div class="flex justify-between py-1">
            <span class="text-gray-400">Authentication:</span>
            <span class="font-mono text-emerald-400">JWT + Bcrypt (Active)</span>
          </div>
        </div>
      </div>

      <div class="text-center pt-4">
        <button onclick="handleLogout()" class="btn-secondary text-red-400 border-red-500/30 hover:bg-red-500/10">
          Sign Out of Account
        </button>
      </div>
    </div>
  `;
}

// 6. Login & Register Pages
function renderLogin() {
  return `
    <div class="animate-fade-in max-w-md mx-auto px-4 py-16">
      <div class="glass-panel p-8 space-y-6">
        <div class="text-center space-y-2">
          <h2 class="text-2xl font-extrabold text-white">Welcome Back</h2>
          <p class="text-sm text-gray-400">Sign in to access your student chat history</p>
        </div>

        <form onsubmit="handleLoginSubmit(event)" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-300 mb-1">Email Address</label>
            <input id="loginEmail" type="email" value="student@college.edu" required class="w-full bg-gray-950 border border-gray-800 focus:border-indigo-500 text-white rounded-xl px-4 py-2.5 text-sm outline-none" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-300 mb-1">Password</label>
            <input id="loginPassword" type="password" value="Student@123" required class="w-full bg-gray-950 border border-gray-800 focus:border-indigo-500 text-white rounded-xl px-4 py-2.5 text-sm outline-none" />
          </div>
          <button type="submit" class="btn-primary w-full py-2.5 justify-center mt-2">Sign In</button>
        </form>

        <div class="text-center text-xs text-gray-400">
          Don't have an account? <span onclick="navigate('register')" class="text-indigo-400 hover:underline cursor-pointer font-semibold">Register</span>
        </div>
      </div>
    </div>
  `;
}

function renderRegister() {
  return `
    <div class="animate-fade-in max-w-md mx-auto px-4 py-16">
      <div class="glass-panel p-8 space-y-6">
        <div class="text-center space-y-2">
          <h2 class="text-2xl font-extrabold text-white">Create Student Account</h2>
          <p class="text-sm text-gray-400">Get 24/7 AI academic advising support</p>
        </div>

        <form onsubmit="handleRegisterSubmit(event)" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-300 mb-1">Full Name</label>
            <input id="regName" type="text" placeholder="John Doe" required class="w-full bg-gray-950 border border-gray-800 focus:border-indigo-500 text-white rounded-xl px-4 py-2.5 text-sm outline-none" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-300 mb-1">Email Address</label>
            <input id="regEmail" type="email" placeholder="john@college.edu" required class="w-full bg-gray-950 border border-gray-800 focus:border-indigo-500 text-white rounded-xl px-4 py-2.5 text-sm outline-none" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-300 mb-1">Password</label>
            <input id="regPassword" type="password" placeholder="Minimum 6 characters" required class="w-full bg-gray-950 border border-gray-800 focus:border-indigo-500 text-white rounded-xl px-4 py-2.5 text-sm outline-none" />
          </div>
          <button type="submit" class="btn-primary w-full py-2.5 justify-center mt-2">Create Account</button>
        </form>

        <div class="text-center text-xs text-gray-400">
          Already registered? <span onclick="navigate('login')" class="text-indigo-400 hover:underline cursor-pointer font-semibold">Sign In</span>
        </div>
      </div>
    </div>
  `;
}

// ----------------------------------------------------
// Main Render Function
// ----------------------------------------------------
function render() {
  renderNav();
  const root = document.getElementById('app');
  if (!root) return;

  switch (state.currentView) {
    case 'chat':
      if (!state.token) {
        navigate('login');
        return;
      }
      root.innerHTML = renderChat();
      break;
    case 'documents':
      root.innerHTML = renderDocuments();
      break;
    case 'admin':
      if (state.user?.role !== 'admin') {
        navigate('home');
        return;
      }
      root.innerHTML = renderAdmin();
      break;
    case 'settings':
      root.innerHTML = renderSettings();
      break;
    case 'login':
      root.innerHTML = renderLogin();
      break;
    case 'register':
      root.innerHTML = renderRegister();
      break;
    case 'home':
    default:
      root.innerHTML = renderHome();
      break;
  }
}

// ----------------------------------------------------
// Action Handlers
// ----------------------------------------------------

async function handleLoginSubmit(e) {
  e.preventDefault();
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  try {
    const data = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setToken(data.access_token, data.user);
    navigate('chat');
  } catch (err) {
    alert(err.message);
  }
}

async function quickLogin(email, password) {
  try {
    const data = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setToken(data.access_token, data.user);
    navigate('chat');
  } catch (err) {
    alert(err.message);
  }
}

async function handleRegisterSubmit(e) {
  e.preventDefault();
  const name = document.getElementById('regName').value;
  const email = document.getElementById('regEmail').value;
  const password = document.getElementById('regPassword').value;
  try {
    const data = await request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
    setToken(data.access_token, data.user);
    navigate('chat');
  } catch (err) {
    alert(err.message);
  }
}

function handleLogout() {
  setToken(null, null);
  navigate('home');
}

// Chat Actions
async function loadConversationsList() {
  if (!state.token) return;
  try {
    const convs = await request('/chat/conversations');
    state.conversations = convs;
    const listEl = document.getElementById('conversationList');
    if (listEl) listEl.innerHTML = renderConversationItems();
  } catch (err) {
    console.error(err);
  }
}

async function loadConversation(id) {
  state.currentConversationId = id;
  try {
    const data = await request(`/chat/conversations/${id}`);
    state.messages = data.messages || [];
    render();
    scrollToBottom();
  } catch (err) {
    console.error(err);
  }
}

async function createNewChat() {
  state.currentConversationId = null;
  state.messages = [];
  render();
}

async function handleDeleteConversation(id) {
  if (!confirm('Are you sure you want to delete this chat?')) return;
  try {
    await request(`/chat/conversations/${id}`, { method: 'DELETE' });
    state.conversations = state.conversations.filter(c => c.id !== id);
    if (state.currentConversationId === id) {
      state.currentConversationId = null;
      state.messages = [];
    }
    render();
  } catch (err) {
    alert(err.message);
  }
}

function askPresetQuestion(text) {
  const input = document.getElementById('chatInput');
  if (input) {
    input.value = text;
    handleSendMessage(new Event('submit'));
  }
}

async function handleSendMessage(e) {
  if (e) e.preventDefault();
  const input = document.getElementById('chatInput');
  if (!input) return;
  const query = input.value.trim();
  if (!query) return;
  input.value = '';

  if (!state.token) {
    navigate('login');
    return;
  }

  // Push user message to UI immediately
  state.messages.push({
    id: 'temp-' + Date.now(),
    role: 'user',
    content: query,
    createdAt: new Date().toISOString()
  });
  state.isStreaming = true;
  render();
  scrollToBottom();

  try {
    const res = await request('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: query,
        conversationId: state.currentConversationId,
        language: state.selectedLanguage,
        department: state.selectedDepartment
      })
    });

    state.isStreaming = false;
    state.currentConversationId = res.conversationId;
    state.messages.push({
      id: res.messageId,
      role: 'assistant',
      content: res.answer,
      sources: res.sources || [],
      createdAt: new Date().toISOString()
    });
    render();
    scrollToBottom();
    loadConversationsList();
  } catch (err) {
    state.isStreaming = false;
    state.messages.push({
      id: 'err-' + Date.now(),
      role: 'assistant',
      content: `❌ Error: ${err.message}`,
      sources: [],
      createdAt: new Date().toISOString()
    });
    render();
    scrollToBottom();
  }
}

function scrollToBottom() {
  const container = document.getElementById('messagesContainer');
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

// Feedback
async function handleFeedback(messageId, rating, reason = '', comment = '') {
  try {
    await request('/feedback', {
      method: 'POST',
      body: JSON.stringify({ messageId, rating, reason, comment })
    });
    alert('Thank you for your feedback! It helps improve the college knowledge base.');
    closeModal();
  } catch (err) {
    alert(err.message);
  }
}

function openFeedbackModal(messageId) {
  const modal = document.getElementById('modalContainer');
  if (!modal) return;
  modal.innerHTML = `
    <div class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
      <div class="glass-panel p-6 max-w-md w-full space-y-4">
        <h3 class="text-lg font-bold text-white">Answer Feedback</h3>
        <p class="text-xs text-gray-400">Help us understand why this answer wasn't helpful:</p>
        <select id="fbReason" class="w-full bg-gray-950 border border-gray-800 text-white rounded-xl px-3 py-2 text-sm">
          <option value="Incorrect information">Incorrect information</option>
          <option value="Missing information">Missing information</option>
          <option value="Irrelevant source cited">Irrelevant source cited</option>
          <option value="Answer not clear">Answer not clear</option>
          <option value="Other">Other</option>
        </select>
        <textarea id="fbComment" placeholder="Additional details (optional)..." class="w-full bg-gray-950 border border-gray-800 text-white rounded-xl p-3 text-sm h-20 outline-none"></textarea>
        <div class="flex justify-end gap-2">
          <button onclick="closeModal()" class="btn-secondary text-xs">Cancel</button>
          <button onclick="submitFeedbackFromModal('${messageId}')" class="btn-primary text-xs">Submit Feedback</button>
        </div>
      </div>
    </div>
  `;
}

function submitFeedbackFromModal(messageId) {
  const reason = document.getElementById('fbReason')?.value || '';
  const comment = document.getElementById('fbComment')?.value || '';
  handleFeedback(messageId, -1, reason, comment);
}

function closeModal() {
  const modal = document.getElementById('modalContainer');
  if (modal) modal.innerHTML = '';
}

// Document Management
async function loadDocumentsList() {
  try {
    const docs = await request('/documents');
    state.documents = docs;
    const tableBody = document.getElementById('documentTableBody');
    if (tableBody) {
      tableBody.innerHTML = renderDocumentRows();
    }
  } catch (err) {
    console.error(err);
  }
}

function openUploadModal() {
  const modal = document.getElementById('modalContainer');
  if (!modal) return;
  modal.innerHTML = `
    <div class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
      <div class="glass-panel p-6 max-w-lg w-full space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-bold text-white">Upload Knowledge Document</h3>
          <button onclick="closeModal()" class="text-gray-400 hover:text-white">✕</button>
        </div>
        <form onsubmit="handleDocUploadSubmit(event)" class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-gray-300 mb-1">File (PDF, DOCX, TXT)</label>
            <input id="uploadFile" type="file" required accept=".pdf,.docx,.txt" class="w-full text-xs text-gray-400 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:bg-indigo-600 file:text-white hover:file:bg-indigo-700" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-300 mb-1">Document Title</label>
            <input id="docTitle" type="text" placeholder="e.g. Academic Examination Regulations 2026" required class="w-full bg-gray-950 border border-gray-800 text-white rounded-xl px-3 py-2 text-sm outline-none" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1">Category</label>
              <select id="docCategory" class="w-full bg-gray-950 border border-gray-800 text-white rounded-xl px-3 py-2 text-xs">
                <option value="General FAQ">General FAQ</option>
                <option value="Admissions">Admissions</option>
                <option value="Academics">Academics</option>
                <option value="Exams">Exams</option>
                <option value="Fees">Fees</option>
                <option value="Hostel">Hostel</option>
                <option value="Placements">Placements</option>
                <option value="Scholarships">Scholarships</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1">Academic Year</label>
              <input id="docYear" type="text" value="2026" class="w-full bg-gray-950 border border-gray-800 text-white rounded-xl px-3 py-2 text-xs outline-none" />
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-300 mb-1">Description</label>
            <textarea id="docDesc" placeholder="Brief summary of what this document covers..." class="w-full bg-gray-950 border border-gray-800 text-white rounded-xl p-2.5 text-xs h-16 outline-none"></textarea>
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" onclick="closeModal()" class="btn-secondary text-xs">Cancel</button>
            <button type="submit" class="btn-primary text-xs">Upload & Process</button>
          </div>
        </form>
      </div>
    </div>
  `;
}

async function handleDocUploadSubmit(e) {
  e.preventDefault();
  const fileInput = document.getElementById('uploadFile');
  if (!fileInput.files[0]) return;

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('title', document.getElementById('docTitle').value);
  formData.append('category', document.getElementById('docCategory').value);
  formData.append('academic_year', document.getElementById('docYear').value);
  formData.append('description', document.getElementById('docDesc').value);

  closeModal();

  try {
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${state.token}` },
      body: formData
    });
    if (!res.ok) throw new Error('Upload failed');
    alert('Document uploaded! Processing and vector chunking started in background.');
    loadDocumentsList();
  } catch (err) {
    alert(err.message);
  }
}

async function handleReprocessDoc(id) {
  try {
    await request(`/documents/${id}/reprocess`, { method: 'POST' });
    alert('Reprocessing initiated!');
    loadDocumentsList();
  } catch (err) {
    alert(err.message);
  }
}

async function handleDeleteDoc(id) {
  if (!confirm('Are you sure you want to delete this document and remove its vectors?')) return;
  try {
    await request(`/documents/${id}`, { method: 'DELETE' });
    loadDocumentsList();
  } catch (err) {
    alert(err.message);
  }
}

// Admin Data
async function loadAdminData() {
  try {
    const [analytics, unanswered] = await Promise.all([
      request('/admin/analytics'),
      request('/admin/unanswered?status=open')
    ]);
    state.analytics = analytics;
    state.unansweredQuestions = unanswered;
    render();
  } catch (err) {
    console.error(err);
  }
}

async function handleResolveUnanswered(id) {
  try {
    await request(`/admin/unanswered/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ status: 'resolved', adminNotes: 'Addressed via uploaded documentation' })
    });
    loadAdminData();
  } catch (err) {
    alert(err.message);
  }
}

// Initial Bootstrapping
function initApp() {
  const initialPath = window.location.pathname.replace('/', '') || 'home';
  navigate(initialPath);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
