// API Service - Backend Integration
import * as XLSX from 'xlsx';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Get stored auth token
const getAuthToken = () => localStorage.getItem('authToken');

// API request helper with auth and error handling
const apiRequest = async (endpoint, options = {}) => {
  const token = getAuthToken();
  
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || `HTTP error ${response.status}`);
    }
    
    return { success: true, ...data };
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    return { success: false, error: error.message || 'Network error' };
  }
};

// Required columns for Excel parsing
const REQUIRED_COLUMNS = [
  'Conversation ID',
  'Channel',
  'Created Date',
  'Customer Role',
  'Agent Name',
  'Product',
  'Account_Name',
  'Transcript',
  'Property_Name',
  'Property_City',
  'Property_State',
  'Contact_Name',
  'Contact_Role',
  'Contact_Phone'
];

// ============================================
// Authentication APIs
// ============================================
export const authAPI = {
  login: async (credentials, userType) => {
    const response = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password,
        user_type: userType, // 'user' or 'agent'
      }),
    });

    if (response.success && response.token) {
      localStorage.setItem('authToken', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }

    return response;
  },

  logout: async () => {
    const response = await apiRequest('/auth/logout', { method: 'POST' });
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    return response;
  },

  };

// ============================================
// Ticket Management APIs
// ============================================
export const caseAPI = {
  // Parse Excel file locally (client-side)
  uploadFile: async (file) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
          
          if (jsonData.length < 2) {
            resolve({ success: false, error: 'Excel file is empty or has no data rows' });
            return;
          }
          
          const headers = jsonData[0].map(h => h?.toString().trim() || '');
          
          const columnMap = {};
          REQUIRED_COLUMNS.forEach(col => {
            const index = headers.findIndex(h => h.toLowerCase() === col.toLowerCase());
            columnMap[col] = index;
          });
          
          const missingColumns = REQUIRED_COLUMNS.filter(col => columnMap[col] === -1);
          if (missingColumns.length > 0) {
            resolve({ success: false, error: `Missing required columns: ${missingColumns.join(', ')}` });
            return;
          }
          
          const parsedData = [];
          for (let i = 1; i < jsonData.length; i++) {
            const row = jsonData[i];
            if (!row || row.length === 0) continue;
            
            const record = {
              id: i,
              conversationId: row[columnMap['Conversation ID']]?.toString() || '',
              channel: row[columnMap['Channel']]?.toString() || '',
              createdDate: row[columnMap['Created Date']]?.toString() || '',
              customerRole: row[columnMap['Customer Role']]?.toString() || '',
              agentName: row[columnMap['Agent Name']]?.toString() || '',
              product: row[columnMap['Product']]?.toString() || '',
              accountName: row[columnMap['Account_Name']]?.toString() || '',
              transcript: row[columnMap['Transcript']]?.toString() || '',
              propertyName: row[columnMap['Property_Name']]?.toString() || '',
              propertyCity: row[columnMap['Property_City']]?.toString() || '',
              propertyState: row[columnMap['Property_State']]?.toString() || '',
              contactName: row[columnMap['Contact_Name']]?.toString() || '',
              contactRole: row[columnMap['Contact_Role']]?.toString() || '',
              contactPhone: row[columnMap['Contact_Phone']]?.toString() || '',
            };
            
            const missingFields = [];
            Object.entries(record).forEach(([key, value]) => {
              if (key !== 'id' && key !== 'missingFields' && key !== 'isValid' && !value) {
                missingFields.push(key);
              }
            });
            
            record.missingFields = missingFields;
            record.isValid = missingFields.length === 0;
            parsedData.push(record);
          }
          
          resolve({
            success: true,
            parsedData,
            totalRows: parsedData.length,
            validRows: parsedData.filter(r => r.isValid).length,
            invalidRows: parsedData.filter(r => !r.isValid).length,
          });
        } catch (error) {
          console.error('Error parsing Excel file:', error);
          resolve({ success: false, error: 'Failed to parse Excel file. Please check the file format.' });
        }
      };
      
      reader.onerror = () => resolve({ success: false, error: 'Failed to read file' });
      reader.readAsArrayBuffer(file);
    });
  },

  // Submit tickets to backend for RAG processing
  submitTickets: async (tickets) => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    const payload = {
      tickets: tickets.map(t => ({
        conversation_id: t.conversationId,
        channel: t.channel,
        created_date: t.createdDate,
        customer_role: t.customerRole,
        agent_name: t.agentName,
        product: t.product,
        account_name: t.accountName,
        transcript: t.transcript,
        property_name: t.propertyName,
        property_city: t.propertyCity,
        property_state: t.propertyState,
        contact_name: t.contactName,
        contact_role: t.contactRole,
        contact_phone: t.contactPhone,
      })),
      submitted_by: user.id || 'unknown',
    };

    return apiRequest('/tickets/upload', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Get tickets assigned to agent
  getAgentTickets: async (agentId) => {
    return apiRequest(`/tickets?agent_id=${agentId}`);
  },

  // Get pending tickets for agent
  getPendingCases: async (agentId) => {
    return apiRequest(`/tickets/pending${agentId ? `?agent_id=${agentId}` : ''}`);
  },

  // Get resolved tickets
  getResolvedCases: async (agentId) => {
    return apiRequest(`/tickets/resolved${agentId ? `?agent_id=${agentId}` : ''}`);
  },

  // Get single ticket by ID
  getTicketById: async (ticketId) => {
    return apiRequest(`/tickets/${ticketId}`);
  },

  // Search tickets using RAG
  searchCases: async (query) => {
    return apiRequest(`/rag/search?q=${encodeURIComponent(query)}`);
  },

  // Update ticket status (approve/reject/edit)
  updateCaseStatus: async (ticketId, status, resolution) => {
    return apiRequest(`/tickets/${ticketId}`, {
      method: 'PATCH',
      body: JSON.stringify({
        status,
        edited_resolution: resolution,
      }),
    });
  },
};

// ============================================
// Knowledge Base APIs
// ============================================
export const knowledgeAPI = {
  // Get all knowledge articles
  getArticles: async () => {
    return apiRequest('/knowledge');
  },

  // Get single knowledge article
  getArticleById: async (articleId) => {
    return apiRequest(`/knowledge/${articleId}`);
  },

  // Add resolution to knowledge base
  addToKnowledgeBase: async (ticketData) => {
    return apiRequest('/knowledge', {
      method: 'POST',
      body: JSON.stringify({
        ticket_id: ticketData.ticketId,
        conversation_id: ticketData.conversationId,
        product: ticketData.product,
        resolution: ticketData.resolution,
        reference_articles: ticketData.referenceArticles,
      }),
    });
  },

  // Search knowledge base (semantic search)
  searchKnowledge: async (query) => {
    return apiRequest(`/knowledge/search?q=${encodeURIComponent(query)}`);
  },
};

// ============================================
// RAG / AI APIs
// ============================================
export const ragAPI = {
  // Generate AI resolution for a ticket
  generateResolution: async (ticketId) => {
    return apiRequest('/rag/generate', {
      method: 'POST',
      body: JSON.stringify({ ticket_id: ticketId }),
    });
  },

  // Search similar cases
  searchSimilar: async (query) => {
    return apiRequest(`/rag/search?q=${encodeURIComponent(query)}`);
  },
};

// ============================================
// Chatbot APIs
// ============================================
export const chatbotAPI = {
  sendMessage: async (message, context = {}) => {
    return apiRequest('/chatbot/message', {
      method: 'POST',
      body: JSON.stringify({
        message,
        context: {
          ticket_id: context.ticketId,
          previous_messages: context.previousMessages || [],
        },
      }),
    });
  },
};

// ============================================
// Export all APIs
// ============================================
export default {
  auth: authAPI,
  cases: caseAPI,
  knowledge: knowledgeAPI,
  rag: ragAPI,
  chatbot: chatbotAPI,
};
