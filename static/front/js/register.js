// 使用面向对象的方法来编写js代码
// 面向对象

var RegisterHandler = function (){
//     相当于构造函数
}

RegisterHandler.prototype.listenSendCaptchaEvent = function(){
    var callback = function (event){
        // 将原声的js对象变成jq对象
        var $this = $(this);
        event.preventDefault(); // 阻止默认的点击事件
        var email = $("input[name=email]").val(); // 获取传进来的email的值
        var reg = /^\w+((.\w+)|(-\w+))@[A-Za-z0-9]+((.|-)[A-Za-z0-9]+).[A-Za-z0-9]+$/;  // 验证邮箱格式的正则
        if (!email || !reg.test(email)){  // 如果邮箱不存在, 或者邮箱没通过验证
            messageBox.showInfo("请输入正确的邮箱地址");
            return;
        }
    //     如果满足就要去发送ajax请求, 调用ajax的get方法进行发送请求
        zlajax.get({
            url: "/email/captcha?email=" + email,
            success: function (result){
                if (result['code'] == 200){
                    console.log("邮件发送成功");
                //     发送成功了, 开始验证码按钮的倒计时
                //     先取消按钮的点击事件
                    $this.off("click")
                    // 添加一个class属性
                    $this.addClass("disabled");
                //   开始倒计时
                    var countdown = 10;
                    var interval = setInterval(function (){
                        if (countdown>0){
                            $this.text(countdown)
                        }else {
                            $this.text("发送验证码");
                            $this.removeClass("disabled");
                            $this.on("click", callback);
                            // 清理定时器
                            clearInterval(interval)
                        }
                        countdown--;

                    }, 1000)

                } else {
                    console.log(result['message']);
                }

            }
        })


    }
    $("#email-captcha-btn").on("click", callback)
}


RegisterHandler.prototype.listenGraphCaptchaEvent = function (){
    $("#captcha-img").on("click", function () {
        console.log("点击了图形验证码")
    //     刷新验证码, 再次调用这个接口url就可以
        var $this = $(this);
        var src = $this.attr("src");
        //  /graph/captcha?sign=Math.random()
        let new_src = zlparam.setParam(src, "sign", Math.random());
        $this.attr("src", new_src);
    });
}

RegisterHandler.prototype.listenSubmitEvent = function (){
    $("#submit-btn").on("click", function (event) {
        console.log("点击了立即注册按钮")
        event.preventDefault(); // 阻止默认的点击事件
        var email = $("input[name=email]").val(); // 获取传进来的email的值
        var email_captcha = $("input[name=email_captcha]").val(); // 获取传进来的email的值

        var username = $("input[name=username]").val(); // 获取传进来的email的值
        var password = $("input[name=password]").val(); // 获取传进来的email的值
        var repeat_password = $("input[name=repeat_password]").val(); // 获取传进来的email的值
        var graph_captcha = $("input[name=graph_captcha]").val(); // 获取传进来的email的值

        if (!email || !email_captcha || !username || !password || !repeat_password || !graph_captcha){
            console.log("请填写完整的注册信息");
            return;
        }
        // 发送ajax请求
        zlajax.post({
            data: {
                "email": email,
                "email_captcha": email_captcha,
                "username": username,
                "password": password,
                "repeat_password": repeat_password,
                "graph_captcha": graph_captcha
            },
            success: function (result) {
                if (result['code'] == 200){
                    console.log("注册成功");
                    window.location = "/login"
                } else {
                    alert(result['message']);
                }

            }
        })



    });
}


RegisterHandler.prototype.run = function (){
    this.listenSendCaptchaEvent()
    this.listenGraphCaptchaEvent()
    this.listenSubmitEvent()
}

// id="email-captcha-btn"
// jQuery(function(){})
$(function(){
    var handler = new RegisterHandler();
    handler.run()
})