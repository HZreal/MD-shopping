let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        is_show_edit: false,                      // 编辑框是否关闭
        // 用户表单数据，用于用户新增或者修改收货地址
        form_address: {
            receiver: '',                       // 收货人
            // vue绑定了select下option的value属性
            province_id: '',                    // 省
            city_id: '',                        // 市
            district_id: '',                    // 区县
            place: '',                          // 详细地址
            mobile: '',
            tel: '',
            email: '',
        },

        provinces: [],                          // 存储后端查库传来的省数据(数组,元素为省对象)
        cities: [],                             // 某省下的所有市
        districts: [],                          // 某市下的所有区县

        // 后端通过jinja2传给js再传给vue的用户地址信息
        addresses: JSON.parse(JSON.stringify(addresses)),              // 将jinja2传来的字典列表转成列表/数组格式的字符串，再用Json.parse解析成js可识别的数组或对象数据
        default_address_id: parseInt(JSON.parse(JSON.stringify(default_address_id))),                        // 将后端传来的默认地址id转成int

        // 字符串类型的下标索引：当前需要编辑的address对象在addresses数组中的下标index(整型)转成字符串类型
        editing_address_index: '',                                     // editing_address_index = index.toString()
        edit_title_index: '',                                          // 字符串类型的下标索引，与上作用等同
        // 接收输入框用户输入的新收货地址标题
        new_title: '',

        // 表单是否显示错误信息
        error_receiver: false,
        error_place: false,
        error_mobile: false,
        error_tel: false,
        error_email: false,
    },

    // 加载完页面就获取省份数据
    mounted() {
        // 获取省份数据
        this.get_provinces();
    },

    watch: {
        // 监听到省份id变化：即用户一选择某个省则立即axios请求该省下所有市的数据
        'form_address.province_id': function(){
            if (this.form_address.province_id) {
                let url = '/areas/?area_id=' + this.form_address.province_id;
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.code == '0') {
                            this.cities = response.data.sub_data.subs;             // 取得该省下的所有市
                        } else {
                            console.log(response.data);
                            this.cities = [];
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                        this.cities = [];
                    })
            }
        },
        // 监听到城市id变化
        'form_address.city_id': function(){
            if (this.form_address.city_id){
                let url = '/areas/?area_id='+ this.form_address.city_id;
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.code == '0') {
                            this.districts = response.data.sub_data.subs;             // 取得该市下的所有区县
                        } else {
                            console.log(response.data);
                            this.districts = [];
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                        this.districts = [];
                    })
            }
        }
    },
    methods: {
        // 展示新增地址弹框
        show_add_site(){
            this.is_show_edit = true;                      // 编辑框展示
            this.clear_all_errors();                       // 清空错误提示信息

            // 清空原有数据
            this.form_address.receiver = '';
            this.form_address.province_id = '';
            this.form_address.city_id = '';
            this.form_address.district_id = '';
            this.form_address.place = '';
            this.form_address.mobile = '';
            this.form_address.tel = '';
            this.form_address.email = '';
            this.editing_address_index = '';
        },

        // 展示编辑地址弹框：需要传参：需要传参index，为当前address对象在addresses数组中的下标索引
        show_edit_site(index){
            this.is_show_edit = true;                                    // 编辑框展示
            this.clear_all_errors();                                     // 清空错误提示信息
            this.editing_address_index = index.toString();               // 下标索引转字符串
            // TODO 弹出编辑框时，将当前address对象(js数据)转成json数据，再解析成对象数据，从而显示在表单编辑框中
            // JSON.parse(JSON.stringify(obj))我们一般用来深拷贝，其过程说白了就是利用JSON.stringify将js对象序列化(JSON字符串)，再使用JSON.parse来反序列化(还原)js对象；
            // 序列化的作用是存储(对象本身存储的只是一个地址映射，如果断电，对象将不复存在，因此需将对象的内容转换成字符串的形式再保存在磁盘上 )和传输（例如 如果请求的Content-Type是 application/x-www-form-urlencoded，则前端这边需要使用qs.stringify(data)来序列化参数再传给后端，否则后端接受不到； ps: Content-Type 为 application/json;charset=UTF-8或者 multipart/form-data 则可以不需要 ）
            this.form_address = JSON.parse(JSON.stringify(this.addresses[index]));              // JSON.stringify()方法用于将js数据(对象或数组)转换为JSON字符串，
        },

        // 校验收货人
        check_receiver(){
            if (!this.form_address.receiver) {
                this.error_receiver = true;
            } else {
                this.error_receiver = false;
            }
        },
        // 校验收货地址
        check_place(){
            if (!this.form_address.place) {
                this.error_place = true;
            } else {
                this.error_place = false;
            }
        },
        // 校验手机号
        check_mobile(){
            let re = /^1[34578]\d{9}$/;
            if(re.test(this.form_address.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile = true;
            }
        },
        // 校验固定电话
        check_tel(){
            if (this.form_address.tel) {
                let re = /^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$/;
                if (re.test(this.form_address.tel)) {
                    this.error_tel = false;
                } else {
                    this.error_tel = true;
                }
            } else {
                this.error_tel = false;
            }
        },
        // 校验邮箱
        check_email(){
            if (this.form_address.email) {
                let re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
                if(re.test(this.form_address.email)) {
                    this.error_email = false;
                } else {
                    this.error_email = true;
                }
            } else {
                this.error_email = false;
            }
        },
        // 清空错误提示信息
        clear_all_errors(){
            this.error_receiver = false;
            this.error_mobile = false;
            this.error_place = false;
            this.error_tel = false;
            this.error_email = false;
        },
        // 获取省份数据(页面加载完成就要执行获取)
        get_provinces(){
            let url = '/areas/';                      // 不携带查询参数area_id
            axios.get(url, {
                responseType: 'json'
            })
                .then(response => {
                    if (response.data.code == '0') {
                        this.provinces = response.data.province_list;
                    } else {
                        console.log(response.data);
                        this.provinces = [];
                    }
                })
                .catch(error => {
                    console.log(error.response);
                    this.provinces = [];
                })
        },

        // 新增or修改地址：点击表单新增按钮触发
        save_address(){
            if (this.error_receiver || this.error_place || this.error_mobile || this.error_email || !this.form_address.province_id || !this.form_address.city_id || !this.form_address.district_id ) {
                alert('信息填写有误！');
            }
            else {
                // 注意：0 == '';返回true，因为值相等;       0 === '';返回false，因为值相等但数据类型不同，不全等;
                // ！！！修改地址时，会传入当前地址的下标index，而当index=0时，由于在js里 0 == '' 为逻辑true，所以无法区分是新增数据还是修改数据
                // 为了避免在第0个索引处冲突，我们选择this.editing_address_index === ''的方式进行判断
                if (this.editing_address_index === '') {
                    // 新增地址
                    let url = '/addresses/create/';
                    axios.post(url, this.form_address, {
                        headers: {
                            'X-CSRFToken':getCookie('csrftoken')
                        },
                        responseType: 'json'
                    }).then(response => {
                            if (response.data.code == '0') {
                                // 局部刷新界面：展示所有地址信息，将新的地址添加到头部
                                this.addresses.splice(0, 0, response.data.address);
                                this.is_show_edit = false;
                            }
                            else if (response.data.code == '4101') {
                                location.href = '/login/?next=/addresses/';
                            }
                            else {
                                alert(response.data.errmsg);
                            }
                        }).catch(error => {
                            console.log(error.response);
                        })
                }
                else {
                    // 修改地址
                    let url = '/addresses/' + this.addresses[this.editing_address_index].id + '/';
                    axios.put(url, this.form_address, {
                        headers: {
                            'X-CSRFToken':getCookie('csrftoken')
                        },
                        responseType: 'json'
                    }).then(response => {
                            if (response.data.code == '0') {
                                this.addresses[this.editing_address_index] = response.data.address;
                                this.is_show_edit = false;
                            }
                            else if (response.data.code == '4101') {
                                location.href = '/login/?next=/addresses/';
                            }
                            else {
                                alert(response.data.errmsg);
                            }
                        }).catch(error => {
                            alert(error.response);
                        })
                }
            }
        },

        // 删除地址：需要传参index，为当前address在addresses数组中的下标索引
        delete_address(index){
            let url = '/addresses/' + this.addresses[index].id + '/';
            axios.delete(url, {
                headers: {
                    'X-CSRFToken':getCookie('csrftoken')
                },
                responseType: 'json'
            }).then(response => {
                    if (response.data.code == '0') {
                        // 删除对应的标签
                        this.addresses.splice(index, 1);
                    }
                    else if (response.data.code == '4101') {
                        location.href = '/login/?next=/addresses/';
                    }
                    else {
                        alert(response.data.errmsg);
                    }
                }).catch(error => {
                    console.log(error.response);
                })
        },

        // 设置默认地址
        set_default(index){
            let url = '/addresses/' + this.addresses[index].id + '/default/';
            axios.put(url, {}, {
                headers: {
                    'X-CSRFToken':getCookie('csrftoken')
                },
                responseType: 'json'
            }).then(response => {
                    if (response.data.code == '0') {
                        // 设置默认地址标签
                        this.default_address_id = this.addresses[index].id;
                    }
                    else if (response.data.code == '4101') {
                        location.href = '/login/?next=/addresses/';
                    }
                    else {
                        alert(response.data.errmsg);
                    }
                }).catch(error => {
                    console.log(error.response);
                })
        },

        // 展示地址title编辑框
        show_edit_title(index){
            this.edit_title_index = index;
        },
        // 取消保存地址title
        cancel_title(){
            this.edit_title_index = '';
            this.new_title = '';
        },
        // 修改地址title
        save_title(index){
            if (!this.new_title) {
                alert("请填写标题后再保存！");
            } else {
                let url = '/addresses/' + this.addresses[index].id + '/title/';
                axios.put(url, {
                    title: this.new_title
                }, {
                    headers: {
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    responseType: 'json'
                }).then(response => {
                        if (response.data.code == '0') {
                            // 当响应状态码0表示后端设置成功，直接将用户输入的内容this.new_title传给当前address.title进行页面局部刷新显示
                            this.addresses[index].title = this.new_title;
                            this.cancel_title();
                        }
                        else if (response.data.code == '4101') {
                            location.href = '/login/?next=/addresses/';
                        }
                        else {
                            alert(response.data.errmsg);
                        }
                    }).catch(error => {
                        console.log(error.response);
                    })
            }
        },
    }
});