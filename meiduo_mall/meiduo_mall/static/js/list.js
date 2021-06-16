let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        category_id: category_id,                  //后端将category_id传给js再传到vue
        hot_skus: [],
        cart_total_count: 0,
        carts: [],
    },
    mounted(){
        // 获取热销商品数据
        this.get_hot_skus();
        // 获取简单购物车数据
        this.get_carts();
    },
    methods: {
    	// 获取热销商品数据(页面加载完成后才发送请求获取热销商品数据)
        get_hot_skus(){
            if(this.category_id){                                    // category_id存在则发送axios请求
                let url = '/hot/'+ this.category_id +'/';
                axios.get(url, {
                    responseType: 'json'
                }).then((response) => {
                        this.hot_skus = response.data.hot_skus;               // 成功回调的数据绑定到vue
                        for(let i=0; i<this.hot_skus.length; i++){
                            this.hot_skus[i].url = '/detail/' + this.hot_skus[i].id + '/';
                        }
                    }).catch((error) => {
                        console.log(error.response);
                    })
            }
        },

        // 获取简单购物车数据
        get_carts(){
        	let url = '/carts/simple/';
            axios.get(url, {
                responseType: 'json',
            }).then(response => {
                    this.carts = response.data.cart_skus;
                    this.cart_total_count = 0;
                    for(let i=0;i<this.carts.length;i++){
                        if (this.carts[i].name.length>25){
                            this.carts[i].name = this.carts[i].name.substring(0, 25) + '...';
                        }
                        this.cart_total_count += this.carts[i].count;
                    }
                }).catch(error => {
                    console.log(error.response);
                })
        },
    }
});