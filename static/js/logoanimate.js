$(function(){
    setInterval(
        function(){
            $(".head_logo").animate(
                {
                    left:'420px',
                    opacity:'0.5'
                },
                800,"swing",
                function(){
                    $(".head_logo").animate(
                    {
                        left:"260px",
                        opacity:"1"
                    },1000);
                }
                );},
        5000);
})