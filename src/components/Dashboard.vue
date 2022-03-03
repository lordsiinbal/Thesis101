<template>
  <NavBar/>
  <div class="topContainer ">
      <div class="headerLink container text-white">
          <a v-on:click="violation('24')">Last 24h</a>
          <a v-on:click="violation('7')">7 days</a>
          <a v-on:click="violation('30')">30 days</a>
      </div>
      <div class="subHeaderLink">
          <div class="iconContainer">
              <img src='icons/iconIllegalPark.svg'/>
              <div class="indicator">
                  <h6 class="text-muted">Total Violation</h6>
                  <h4>{{violationNumber}}</h4>
              </div>
          </div>
      </div>
  </div>
  <div class="bottomContainer">
      <div class="headerContainer">
          <h6 class="text-white">Violation Tracker</h6>
          <div class="selectionContainer">
                <div class='selection text-white'>
                    <label>Month</label>
                    <select>
                        <option class="text-center">January</option>
                    </select>
                </div>
                
                <div class='selection text-white'>
                    <label>Road</label>
                    <select>
                        <option class="text-center">All</option>
                    </select>
                </div>
          </div>
      </div>
      <line-chart :data='chartData' class="lineChart"/>
  </div>
  
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import api from '../api';
export default {
components:{
    NavBar
},

data(){
    return{
        roadList:[],
        twentyFour:0,seven:0, thirty:0,
        chartData:[{
                name:'',
                data:{
                    day1:0,
                    day2:0,
                    day3:0,
                    day4:0,
                    day5:0,
                    day6:0,
                    day7:0,
                    day8:0,
                    day9:0,
                    day10:0,
                    day11:0,
                    day12:0,
                    day13:0,
                    day14:0,
                    day15:0,
                    day16:0,
                    day17:0,
                    day18:0,
                    day19:0,
                    day20:0,
                    day21:0,
                    day22:0,
                    day23:0,
                    day24:0,
                    day25:0,
                    day26:0,
                    day27:0,
                    day28:0,
                    day29:0,
                    day30:0,
                    day31:0,
                    
                    
                } 
                },
        ],
        violationNumber:"",
        violationRecord:[
            {   
                violationID:'',
                vehicleID:'',
                roadName:'',
                roadID:'',
                lengthOfViolation:'',
                startDateAndTime:'',
                endDateAndTime:''
            },
        ],
        violationRecord1:[
            {   
                violationID:'',
                vehicleID:'',
                roadName:'',
                roadID:'',
                lengthOfViolation:'',
                startDateAndTime:'',
                endDateAndTime:''
            },
        ],

    }
},
created(){
    this.getViolation();
  },
methods:{
    diff_hours(dt2, dt1){
        var diff =(dt2.getTime() - dt1.getTime()) / 1000;
        diff /= (60 * 60);
        return Math.abs(Math.round(diff));
    },
    violation(days){
        if (days == "24"){
            this.violationNumber= this.twentyFour;
        }
        else if (days == "7"){
            this.violationNumber= this.seven;
        }
        else if (days == "30"){
            this.violationNumber= this.thirty;
        }
    },
    
    hourDifference(){
            const currentDate = new Date();
            var twentyFour=0,seven=0,thirty=0
            for(var ctr=0;ctr<=this.violationRecord.length-1 ; ctr++){
            const violationDate = new Date(this.violationRecord[ctr]['endDateAndTime']);
            var hours = this.diff_hours(currentDate, violationDate)
            if (parseInt(hours)<=24){
                twentyFour=twentyFour+1;
            }
            if(parseInt(hours)<=168){
                seven = seven+1;

            }
            if(parseInt(hours)<=720){
                thirty=thirty+1;

            }
        }
        this.twentyFour=twentyFour;
        this.seven = seven;
        this.thirty=thirty;
    },
    getViolation(){
        api
            .get("/ViolationFetchAll")
            .then((res) => {
            this.violationRecord = res.data;

                
                this.hourDifference();
                this.violation("24");
                this.roadFilter();
            })
    },
    
    roadFilter(){
        
        for(var ctr=0;ctr<this.violationRecord.length;ctr++){
            if(this.roadList.includes(this.violationRecord[ctr]['roadID'])==false){
                this.roadList.push(this.violationRecord[ctr]['roadID']);
                console.log("road",this.roadList);
            }

        }
        console.log("asd",this.roadList);
    },
    // Data(){
    //     for(var ctr=0;ctr<this.roadList.length;ctr++){
    //        if(this.chartData.includes(this.roadList[ctr])){
    //             this.chartData[] = 
    //        }
    //     }

    // },



    
}

}
</script>
<style scoped>
.topContainer{
    border:2px solid #8F8F9C;
    margin:auto;
    max-width: 1160px;
    margin-top:5%;
   border-radius: 20px;
}
.headerLink{
    display:flex;
    justify-content:flex-start;
    width:100%;
    padding:20px;
    border-bottom:2px solid #8F8F9C;
}
.headerLink a{
    padding:10px;
    cursor: pointer;

}
.iconContainer{
    display: flex;
    justify-content: space-evenly;
    margin:auto;
    color:white;
    font-family: 'Roboto';
}
.indicator{
    display:block;
    margin:auto;
    margin-left:10px;
}
.subHeaderLink{
    display: flex;
    justify-content: center;
   padding:20px;

}
.bottomContainer{
    max-width: 1160px;
    margin: auto;
    margin-top:2%;
    margin-bottom:5%;
    border:2px solid #8F8F9C;
    border-radius:20px;
}
.headerContainer{
    display:flex;
    justify-content: space-between;
    padding:10px;
    font-family: 'Roboto';
    border-bottom:2px solid #8F8F9C;
    justify-items: center;
}
.selectionContainer{
    display: flex;
    justify-content: space-between;
    border:none;
}
.selection{
    display: flex;
    width:160px;
    height:min-content;
    text-align:center;
    margin-left:5px;
height:min-content;
border:2px solid #678ADD
}
.selection label{
    padding-left:5px;
    padding-right:5px;
}
select{
    width:100%;
    height:26px;
    background-color:#678ADD;
    border:none;
    color:white;
    margin:auto;
    margin-left:5px;
    cursor: pointer;
    outline:none;
}

.lineChart{
    padding:20px;
}
</style>