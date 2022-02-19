<template>
  <NavBar/>
  <div class="topContainer ">
      <div class="headerLink container text-white">
          <a>Last 24h</a>
          <a>7 days</a>
          <a>30 days</a>
      </div>
      <div class="subHeaderLink">
          <div class="iconContainer">
              <img src='icons/iconIllegalPark.svg'/>
              <div class="indicator">
                  <h6 class="text-muted">Total Violation</h6>
                  <h4>1</h4>
              </div>
          </div>
          <div class="iconContainer">
              <img src='icons/iconRoad.svg'/>
              <div class="indicator">
                  <h6 class="text-muted">Total Violation</h6>
                  <h4>1</h4>
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
export default {
components:{
    NavBar
},
data(){
    return{
        chartData:[{
            name:'January',
            data:{
            week_1:4,
            week_2:26,
            week_3:10,
            week_4:9
            }
            },
            {
            name:'February',
            data:{
            week_1:9,
            week_2:75,
            week_3:24,
            week_4:19
            }
            },
            {
            name:'March',
            data:{
            week_1:12,
            week_2:44,
            week_3:88,
            week_4:55
            }
            }

        ]
    }
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