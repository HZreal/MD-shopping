// 采用ES6语法
// 前端页码注册校验逻辑步骤：
//         1.导入Vue.js库和ajax请求的库
//         2.准备div盒子标签，注明id选择器
//         3.准备js文件(即本文件)，前端校验逻辑(点击事件，获取/失去焦点，数据绑定完成再显示)
//         4.html页面绑定变量、事件等，即在html文件标签中添加实际需求的属性
//         5.js文件定义变量、事件等，实现逻辑

let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],                       // 修改Vue变量的读取语法，避免和Django模板语法冲突
    data: {

        //v-model 接收用户输入信息
        username: '',
        password: '',
        password2: '',
        mobile: '',
        allow: '',

        //v-show 错误信息默认不显示
        error_name: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,

        //error_message 错误提示信息若是固定的，可以使用绑定的变量动态的展示错误提示信息，若固定的直接在标签中写死
        error_name_message: '',
        error_mobile_message: '',

    },

    methods: {
        // 校验用户名
        // test()方法 检查字符串是否与给出的正则表达式模式相匹配，匹配成功返回true，否则返回 false
        check_username(){
            let re = /^[a-zA-Z][0-9a-zA-Z_]{4,19}$/;                       // 首位只能是字母，总长5-20位
            if(re.test(this.username)){
                this.error_name = false;
            }
            else {
                this.error_name_message = '请输入5-20位字符的用户名，首位只能是字母';
                this.error_name = true;
            }
        },
        // 校验密码
        check_password(){
            let re = /^[A-Za-z][A-Za-z0-9]{7,19}$/;                       //首位非数字，总长8-20位
            // if(re.test(this.password)){
            //     this.error_password = false;
            // }else {
            //     this.error_password = true;
            // }
            this.error_password = !re.test(this.password);               //简写
        },
        // 校验确认密码
        check_password2(){
            // if(this.password2 == this.password){
            //     this.error_password2 = false;
            // }
            // else {
            //     this.error_password2 = true;
            // }
            this.error_password2 = this.password2 !== this.password;      //简写
        },
        // 校验手机号
        check_mobile(){
            let re = /^1[34578]\d{9}$/;
            if(re.test(this.mobile)){
                this.error_mobile = false;
            }
            else {
                this.error_mobile_message = '您输入的手机号格式不正确'
                this.error_mobile = true;
            }
        },
        // 校验是否勾选协议
        check_allow(){
            // if(this.allow){               // 勾选与没勾选就是存在不存在
            //     this.error_allow = false;
            // }
            // else {
            //     this.error_allow = true;
            // }
            this.error_allow = !this.allow;
        },
        // 监听表单提交事件
        on_submit(){
            // 对用户全部输入信息校验，刷新获取最新的错误状态
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_allow();
            // 判断只要有一个错误，则拒绝提交
            if(this.error_name == true || this.error_password == true || this.check_password2 == true || this.error_mobile == true || this.error_allow == true){
                window.event.returnValue = false;
            }
        },


    },


});