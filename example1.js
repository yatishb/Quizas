window.addEventListener("load",function() {
 
	var Q = window.Q = Quintus()
    .include("Sprites, Scenes, Input, 2D, Anim, Touch, UI")
    .setup({
		maximize: true
	}).controls()
    .touch();
    
	// Question Card
	Q.UI.QuestionArea = Q.UI.Text.extend('UI.QuestionArea', {
    init: function() {
        this._super({
            color: "white",
            x: 0,
            y: 0
        });
    },
    generate: function() {
        this.p.label = 5;
    },
    getAnswer: function() {
        return 10;
    }
	});
	
	// set scene
	Q.scene("scene1",function(stage) {            
    //current question
    var qContainer = stage.insert(new Q.UI.Container({
        fill: "gray",
        x: 221,
        y: 325,
        border: 2,
        shadow: 3,
        shadowColor: "rgba(0,0,0,0.5)",
        w: 140,
        h: 50
        })
    );
    
    var question = stage.insert(new Q.UI.QuestionArea(),qContainer);    
    question.generate();
	
	// stage scene
	Q.stageScene("scene1");
	
});
     
});