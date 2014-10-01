$(function(){
function getCookie(c_name) {
  if (document.cookie.length>0) { 
    c_start=document.cookie.indexOf(c_name + "=")
        if (c_start!=-1) { 
            c_start=c_start + c_name.length+1 
            c_end=document.cookie.indexOf(";",c_start)
        if (c_end==-1) c_end=document.cookie.length
            return unescape(document.cookie.substring(c_start,c_end))
        } 
  }
    return ""
};
    var my_answrs = getCookie("tempanswr");//alert(my_answrs);
    if (my_answrs!=""){
        $("#my_answr").val(my_answrs);
    };

    $("#crt_sbjct").on("click","#add_qstn",function(){
        var title = ($("#title").val()).replace(/ /g,'');
        var qstn = $("#qstn").val();
        $.ajax({
            type:"post",
            url:"/add_qstn",
            data:{title:title,qstn:qstn},
            dataType:"json",
            success:function(data){
                if (data=='0'){
                    alert('添加失败，请联系管理员！')
                }else{
                    // alert('添加成功！');
                    // $("#title").val('');
                    // $("#qstn").val('');
                    window.location.reload();
                };
            },
            error:function(err){
                alert('添加失败！');
            }
        });
    });

    $("#my_reply").on("click","#my_answr_btn",function(){
        var my_answr =($("#my_answr").val()).replace(/ /g,'');
        var stu_id = $("#stu_id").val();
        var crrnt_sbjt_id = $("#crrnt_sbjt_id").val();
        $.ajax({
            type:"post",
            url:"/add_answr",
            data:{sbjct_id:crrnt_sbjt_id,stu_id:stu_id,answr:my_answr},
            dataType:"json",
            success:function(data){
                if (data=='0'){
                    alert('添加失败，请联系管理员！')
                };
                if (data=='1'){
                    // alert('添加成功！');
                    // $("#my_answr").val('');
                    window.location.reload();
                    // $("#qstn").val('');
                };
                if (data=='2'){
                    alert('你已回答过本课问题，请勿重复回答！');
                };
            },
            error:function(err){
                alert('添加失败！');
            },
        });
    });
    $("#rightside").on("click","#add_my_ask",function(){
        var my_ask = ($("#my_ask").val()).replace(/ /g,'');
        if (my_ask!=""){
            stu_id = $("#stu_id").val();
            $.ajax({
                type:"post",
                url:"/ask_hlp/"+stu_id,
                data:{qstn:my_ask},
                dataType:"json",
                success:function(data){
                    document.cookie="tempanswr="+escape(($("#my_answr").val()).replace(/ /g,''))+";";
                    window.location.reload();
                    // alert("success");
                },
                error:function(err){
                    alert("error");
                }
            });
        }else{
            alert("提交的问题不能为空！")
        };
    });
    $("#rightside").on("click","#sbmt_hlp",function(){
        var crrnt_obj = $(this).siblings();
        var answr = (crrnt_obj.filter("#reply_hlp").first().val()).replace(/ /g,'');
        if (answr!=""){
            $.ajax({
                type:"post",
                url:"/hlp_answr/"+crrnt_obj.filter("#ask_id").first().val()+"/"+$("#stu_id").val(),
                data:{answr:answr},
                dataType:"json",
                success:function(data){
                    document.cookie="tempanswr="+escape(($("#my_answr").val()).replace(/ /g,''))+";";
                    window.location.reload();
                },
                error:function(err){
                    alert('err');
                },
            });
        }else{
            alert("提交的答案不能为空！")
        };
    });
    $("#mgr_nav").on("click","#disp_crt_sbjct",function(){
        $("#main").hide();
        $("#crt_sbjct").show();
    });
    $("#mgr_nav").on("click","#dis_enable_other",function(){
        $.get("/on_off_answr/"+$("#crrnt_sbjt_id").val());
    });


})