// Configurações e variáveis globais
const API_URL = '';
let salesChart = null;
let commissionsChart = null;

// Aplicação Vue
new Vue({
    el: '#app',
    data: {
        // Autenticação
        isLoggedIn: false,
        user: {
            id: null,
            name: '',
            email: '',
            role: '',
            commission_rate: 0,
            commission_type: 'net',
            can_see_ads: false,
            can_see_gateway_fee: false,
            can_see_other_sales: false
        },
        loginForm: {
            email: '',
            password: ''
        },
        
        // UI
        currentPage: 'dashboard',
        isMobileMenuOpen: false,
        selectedPeriod: '30',
        
        // Dashboard
        dashboardData: {
            total_sales: 0,
            total_commission: 0,
            total_gateway_fee: 0,
            total_ad_expense: 0,
            chart_data: []
        },
        
        // Vendas
        salesData: [],
        showNewSaleModal: false,
        editingSale: false,
        saleForm: {
            id: null,
            client: '',
            product: '',
            quantity: 1,
            total_value: 0,
            seller_id: null,
            ad_expense: 0
        },
        
        // Anúncios
        adExpensesData: [],
        showNewAdExpenseModal: false,
        editingAdExpense: false,
        adExpenseForm: {
            id: null,
            seller_id: null,
            value: 0,
            description: ''
        },
        
        // Pagamentos
        paymentsData: [],
        pendingPayments: [],
        confirmedPayments: [],
        showNewPaymentModal: false,
        paymentForm: {
            seller_id: null,
            amount: 0
        },
        
        // Resumo do Vendedor
        sellerSummary: {
            total_commission: 0,
            total_received: 0,
            pending_amount: 0
        },
        
        // Resumo de Vendedores (Admin)
        sellerSummaryData: [],
        
        // Vendedores
        sellersData: [],
        showNewSellerModal: false,
        editingSeller: false,
        sellerForm: {
            id: null,
            name: '',
            email: '',
            password: '',
            commission_rate: 10,
            commission_type: 'net',
            can_see_ads: false,
            can_see_gateway_fee: false,
            can_see_other_sales: false,
            active: true
        },
        
        // Relatórios
        reportDateRange: {
            start: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],
            end: new Date().toISOString().split('T')[0]
        },
        reportData: [],
        reportTotals: {
            total_value: 0,
            gateway_fee: 0,
            ad_expense: 0,
            commission_value: 0
        },
        
        // Configurações
        settings: {
            gatewayFee: 9,
            defaultCommissionRate: 10,
            defaultCommissionType: 'net'
        }
    },
    mounted() {
        // Verificar se o usuário está logado
        this.checkSession();
        
        // Adicionar listener para responsividade
        window.addEventListener('resize', this.handleResize);
        this.handleResize();
    },
    methods: {
        // Autenticação
        async checkSession() {
            try {
                const response = await axios.get(`${API_URL}/api/auth/check-session`);
                if (response.data.authenticated) {
                    this.isLoggedIn = true;
                    this.user = response.data.user;
                    this.loadInitialData();
                }
            } catch (error) {
                console.error('Erro ao verificar sessão:', error);
                this.isLoggedIn = false;
            }
        },
        async login() {
            try {
                const response = await axios.post(`${API_URL}/api/auth/login`, this.loginForm);
                this.isLoggedIn = true;
                this.user = response.data.user;
                this.loadInitialData();
            } catch (error) {
                console.error('Erro ao fazer login:', error);
                alert('Email ou senha incorretos');
            }
        },
        async logout() {
            try {
                await axios.post(`${API_URL}/api/auth/logout`);
                this.isLoggedIn = false;
                this.user = {
                    id: null,
                    name: '',
                    email: '',
                    role: '',
                    commission_rate: 0,
                    commission_type: 'net',
                    can_see_ads: false,
                    can_see_gateway_fee: false,
                    can_see_other_sales: false
                };
            } catch (error) {
                console.error('Erro ao fazer logout:', error);
            }
        },
        
        // Carregamento de Dados
        loadInitialData() {
            this.loadDashboardData();
            
            if (this.user.role === 'admin') {
                this.loadSellersData();
                this.loadSellerSummaryData();
                this.loadPaymentsData();
            } else {
                this.loadSellerSummary();
                this.loadPaymentHistory();
            }
        },
        async loadDashboardData() {
            try {
                const endpoint = this.user.role === 'admin' 
                    ? `/api/admin/dashboard?period=${this.selectedPeriod}`
                    : `/api/seller/dashboard?period=${this.selectedPeriod}`;
                
                const response = await axios.get(`${API_URL}${endpoint}`);
                this.dashboardData = response.data;
                
                // Renderizar gráficos se for admin
                if (this.user.role === 'admin') {
                    this.$nextTick(() => {
                        this.renderSalesBySellerChart();
                        this.renderCommissionsChart();
                    });
                }
            } catch (error) {
                console.error('Erro ao carregar dados do dashboard:', error);
            }
        },
        async loadSalesData() {
            try {
                const endpoint = this.user.role === 'admin' 
                    ? `/api/admin/sales?period=${this.selectedPeriod}`
                    : `/api/seller/sales?period=${this.selectedPeriod}`;
                
                const response = await axios.get(`${API_URL}${endpoint}`);
                this.salesData = response.data;
            } catch (error) {
                console.error('Erro ao carregar dados de vendas:', error);
            }
        },
        async loadAdExpensesData() {
            try {
                const endpoint = this.user.role === 'admin' 
                    ? `/api/admin/ad-expenses?period=${this.selectedPeriod}`
                    : `/api/seller/ad-expenses?period=${this.selectedPeriod}`;
                
                const response = await axios.get(`${API_URL}${endpoint}`);
                this.adExpensesData = response.data;
            } catch (error) {
                console.error('Erro ao carregar dados de anúncios:', error);
            }
        },
        async loadSellersData() {
            try {
                const response = await axios.get(`${API_URL}/api/admin/users`);
                this.sellersData = response.data;
            } catch (error) {
                console.error('Erro ao carregar dados de vendedores:', error);
            }
        },
        async loadSellerSummaryData() {
            try {
                const response = await axios.get(`${API_URL}/api/admin/seller-summary`);
                this.sellerSummaryData = response.data;
            } catch (error) {
                console.error('Erro ao carregar resumo de vendedores:', error);
            }
        },
        async loadPaymentsData() {
            try {
                const response = await axios.get(`${API_URL}/api/admin/payments`);
                this.paymentsData = response.data;
            } catch (error) {
                console.error('Erro ao carregar dados de pagamentos:', error);
            }
        },
        async loadSellerSummary() {
            try {
                const response = await axios.get(`${API_URL}/api/seller/payments/summary`);
                this.sellerSummary = response.data;
            } catch (error) {
                console.error('Erro ao carregar resumo do vendedor:', error);
            }
        },
        async loadPaymentHistory() {
            try {
                const response = await axios.get(`${API_URL}/api/seller/payments/history`);
                this.pendingPayments = response.data.filter(payment => payment.status === 'pending');
                this.confirmedPayments = response.data.filter(payment => payment.status !== 'pending');
            } catch (error) {
                console.error('Erro ao carregar histórico de pagamentos:', error);
            }
        },
        async generateReport() {
            try {
                const endpoint = this.user.role === 'admin' 
                    ? `/api/admin/reports/sales?start_date=${this.reportDateRange.start}&end_date=${this.reportDateRange.end}`
                    : `/api/seller/reports?start_date=${this.reportDateRange.start}&end_date=${this.reportDateRange.end}`;
                
                const response = await axios.get(`${API_URL}${endpoint}`);
                this.reportData = response.data;
                
                // Calcular totais
                this.reportTotals = {
                    total_value: this.reportData.reduce((sum, sale) => sum + sale.total_value, 0),
                    gateway_fee: this.reportData.reduce((sum, sale) => sum + sale.gateway_fee, 0),
                    ad_expense: this.reportData.reduce((sum, sale) => sum + sale.ad_expense, 0),
                    commission_value: this.reportData.reduce((sum, sale) => sum + sale.commission_value, 0)
                };
            } catch (error) {
                console.error('Erro ao gerar relatório:', error);
            }
        },
        
        // Operações CRUD
        async saveSale() {
            try {
                let response;
                const saleData = { ...this.saleForm };
                
                if (this.user.role !== 'admin') {
                    saleData.seller_id = this.user.id;
                }
                
                if (this.editingSale) {
                    response = await axios.put(`${API_URL}/api/seller/sales/${saleData.id}`, saleData);
                } else {
                    response = await axios.post(`${API_URL}/api/seller/sales`, saleData);
                }
                
                this.closeNewSaleModal();
                this.loadSalesData();
                this.loadDashboardData();
            } catch (error) {
                console.error('Erro ao salvar venda:', error);
                alert('Erro ao salvar venda. Verifique os dados e tente novamente.');
            }
        },
        async saveAdExpense() {
            try {
                let response;
                const expenseData = { ...this.adExpenseForm };
                
                if (this.user.role !== 'admin') {
                    expenseData.seller_id = this.user.id;
                }
                
                if (this.editingAdExpense) {
                    response = await axios.put(`${API_URL}/api/seller/ad-expenses/${expenseData.id}`, expenseData);
                } else {
                    response = await axios.post(`${API_URL}/api/seller/ad-expenses`, expenseData);
                }
                
                this.closeNewAdExpenseModal();
                this.loadAdExpensesData();
                this.loadDashboardData();
            } catch (error) {
                console.error('Erro ao salvar gasto com anúncio:', error);
                alert('Erro ao salvar gasto com anúncio. Verifique os dados e tente novamente.');
            }
        },
        async savePayment() {
            try {
                const response = await axios.post(`${API_URL}/api/admin/payments`, this.paymentForm);
                this.closeNewPaymentModal();
                this.loadPaymentsData();
                this.loadSellerSummaryData();
            } catch (error) {
                console.error('Erro ao registrar pagamento:', error);
                alert('Erro ao registrar pagamento. Verifique os dados e tente novamente.');
            }
        },
        async saveSeller() {
            try {
                let response;
                
                if (this.editingSeller) {
                    response = await axios.put(`${API_URL}/api/admin/users/${this.sellerForm.id}`, this.sellerForm);
                } else {
                    response = await axios.post(`${API_URL}/api/admin/users`, this.sellerForm);
                }
                
                this.closeNewSellerModal();
                this.loadSellersData();
            } catch (error) {
                console.error('Erro ao salvar vendedor:', error);
                alert('Erro ao salvar vendedor. Verifique os dados e tente novamente.');
            }
        },
        async saveSettings() {
            try {
                const response = await axios.put(`${API_URL}/api/admin/settings`, this.settings);
                alert('Configurações salvas com sucesso!');
            } catch (error) {
                console.error('Erro ao salvar configurações:', error);
                alert('Erro ao salvar configurações. Tente novamente.');
            }
        },
        async deleteSale(saleId) {
            if (confirm('Tem certeza que deseja excluir esta venda?')) {
                try {
                    await axios.delete(`${API_URL}/api/admin/sales/${saleId}`);
                    this.loadSalesData();
                    this.loadDashboardData();
                } catch (error) {
                    console.error('Erro ao excluir venda:', error);
                    alert('Erro ao excluir venda. Tente novamente.');
                }
            }
        },
        async deleteAdExpense(expenseId) {
            if (confirm('Tem certeza que deseja excluir este gasto com anúncio?')) {
                try {
                    await axios.delete(`${API_URL}/api/admin/ad-expenses/${expenseId}`);
                    this.loadAdExpensesData();
                    this.loadDashboardData();
                } catch (error) {
                    console.error('Erro ao excluir gasto com anúncio:', error);
                    alert('Erro ao excluir gasto com anúncio. Tente novamente.');
                }
            }
        },
        async toggleSellerStatus(seller) {
            try {
                const newStatus = !seller.active;
                await axios.put(`${API_URL}/api/admin/users/${seller.id}`, {
                    active: newStatus
                });
                this.loadSellersData();
            } catch (error) {
                console.error('Erro ao alterar status do vendedor:', error);
                alert('Erro ao alterar status do vendedor. Tente novamente.');
            }
        },
        async confirmPayment(paymentId) {
            try {
                await axios.put(`${API_URL}/api/seller/payments/confirm/${paymentId}`);
                this.loadPaymentHistory();
                this.loadSellerSummary();
            } catch (error) {
                console.error('Erro ao confirmar pagamento:', error);
                alert('Erro ao confirmar pagamento. Tente novamente.');
            }
        },
        async cancelPayment(paymentId) {
            if (confirm('Tem certeza que deseja cancelar este pagamento?')) {
                try {
                    await axios.put(`${API_URL}/api/admin/payments/${paymentId}/cancel`);
        
(Content truncated due to size limit. Use line ranges to read in chunks)