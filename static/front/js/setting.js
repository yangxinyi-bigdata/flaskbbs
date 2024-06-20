var SettingHandler = function () {

}

SettingHandler.prototype.listenAvatarUploadEvent = function () {
    $('#avatar-input').on("change", function () {
       var image = this.files[0];
       var formData = new FormData();
       formData.append("image", image);
       zlajax.post({
           url: "/avatar/upload",
           data: formData,
           // 如果使用jQuery上传, 还需要指定两个参数
           processData: false,
           contentType: false,
           success: function (result) {
               if (result['code'] == 200) {
                   // result { code: 200 "data"
                   var avatar = result["data"]['avatar']
                   var avatar_url = "/media/avatar/" + avatar;
                   $('#avatar-img').attr('src', avatar_url);

               }
               console.log(result);
           }
           })

    });
}


SettingHandler.prototype.listenSubmitEvent = function () {
      $('#submit-btn').on("click", function (event) {
          event.preventDefault();
          var signature = $('#signature-input').val();

          if (!signature) {
              return;
          }
          if (signature && (signature.length > 50 || signature.length < 2)) {
              zlalert.alertInfoToast("签名长度必须在2-50个字符之间");
              return;
          }
          console.log(signature)
          zlajax.post({
              url: "profile/edit",
              data: {signature},
              success:
                  function(result) {
                      if (result['code'] == 200) {
                          alert("修改成功");
                      } else {
                          alert(result['message']);
                      }
                  }

          })

      });
}

SettingHandler.prototype.run = function () {
    this.listenAvatarUploadEvent();
    this.listenSubmitEvent();
}

$(function () {
    var handler = new SettingHandler();
    handler.run();
})