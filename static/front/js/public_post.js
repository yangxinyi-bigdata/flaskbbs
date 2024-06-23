var PublicPostHandler = function (){
  var csrf_token = $("meta[name='csrf-token']").attr("content");
  var editor = new window.wangEditor("#editor");
  editor.config.uploadImgServer = "/post/image/upload";
  editor.config.uploadFileName = "image";
  // 1. 放到请求体中
  // 2. 放到请求头中X-CSRFToken
  // 再和cookie中的csrf_token进行对比
  editor.config.uploadImgHeaders = {
    "X-CSRFToken": csrf_token
  }
  editor.config.uploadImgMaxSize = 1024*1024*5;
  editor.create();
  this.editor = editor;
}


PublicPostHandler.prototype.listenSubmitEvent = function () {
   var that=this;
  $("#submit-btn").on("click", function (event){
    console.log("到这里还正常")
    event.preventDefault();
    var title = $("input[name='title']").val();
    var board_id = $("select[name='board_id']").val();
    var content = that.editor.txt.html();

    zlajax.post({
      url: "/post/public",
      data: {
        title: title,
        board_id: board_id,
        content: content
      },
      success: function (result){
        if(result['code'] == 200){
          alert("发布成功")
          let data = result["data"]
          let id = data["id"]
          window.location = "/post/detail/" + id;
        }else{
          alert(result['message']);
        }
      }
    })
  })
}


PublicPostHandler.prototype.run = function () {
    this.listenSubmitEvent();
}



$(function(){
  var handler = new PublicPostHandler();
  handler.run();
});