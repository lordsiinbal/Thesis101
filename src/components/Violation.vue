<template>
    <div class="container">
<div class="headContainer">
      <div class="text-white">
          <h5 >{{violationNumber}}</h5>
          <h5> Violations</h5>
      </div>
      <div>
                <div class='selection text-white'>
                    <label>Month</label>
                    <select @click="month()" id="monthValue">
                        <option selected value="01" class="text-center">January</option>
                        <option value="02" class="text-center">February</option>
                        <option value="03" class="text-center">March</option>
                        <option value="04" class="text-center">April</option>
                        <option value="05" class="text-center">May</option>
                        <option value="06" class="text-center">June</option>
                        <option value="07" class="text-center">July</option>
                        <option value="08" class="text-center">August</option>
                        <option value="09" class="text-center">September</option>
                        <option value="10" class="text-center">October</option>
                        <option value="11" class="text-center">November</option>
                        <option value="12" class="text-center">December</option>
                    </select>
                </div>
                
                <div class='selection text-white'>
                    <label>Road</label>
                    <select @click="road()" v-model="selectedRoad">
                        <option class="text-center" v-for="item in roadList" :key="item">{{item}}</option>
                    </select>
                </div>
                <div class='selection text-white'>
                    <input v-model="searchQuery" type="search" placeholder="Search"/>
                    <label><img src="icons/iconSearch.svg"/></label>
                </div>
        </div>

  </div>
  <div class="mainContainer">
      <table>
      <tr class="headerColumn text-white">
            <th> Violation Number</th>
            <th> Vehicle ID</th>
            <th> Road Name</th>
            <th>Road ID</th>
            <th> Length of Violation</th>
            <th> Start Time</th>
            <th> End Time</th>
      </tr>
      <tr class="containerValue container text-white" v-for="record in resultQuery()" :key="record.violationID" >
            <td> {{record.violationID}}</td>
            <td> {{record.vehicleID}}</td>
            <td> {{record.roadName}}</td>
            <td> {{record.roadID}}</td>
            <td> {{record.lengthOfViolation}}</td>
            <td> {{record.startDateAndTime}}</td>
            <td> {{record.endDateAndTime}}</td>
      </tr>
  </table>
  </div>
  
    </div>
  
</template>

<script>
import api from '../api';
export default {
created(){
    this.getViolation();

},
// mounted(){
//     this.getViolation();
// },
data(){
    return{
        violationNumber:"",
        searchQuery: null,
        selectedRoad:"All",
        roadList:["All"],
        tempMonth:"",
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
        violationRecordMonth1:[
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
        violationRecordMonth:[
            {   
                violationID:'',
                vehicleID:'',
                roadName:'',
                roadID:'',
                lengthOfViolation:'',
                startDateAndTime:'',
                endDateAndTime:''
            },
        ]
        
    }
},

methods:{
    month(){
        let monthValue=document.getElementById('monthValue').value;
        console.log("finding Month:", monthValue);
        this.violationRecordMonth1= []
        var ctr =0
        for(ctr=0;ctr<this.violationRecord.length;ctr++){
            if(this.violationRecord[ctr]['startDateAndTime'].slice(0,2)==monthValue & this.tempMonth != monthValue){
                this.violationRecordMonth1.push(this.violationRecord[ctr]);
            }
        }
        this.tempMonth= monthValue
        console.log("value 1",this.violationRecordMonth1);
        this.road()
    },
    getViolation(){
        api
            .get("/ViolationFetchAll")
            .then((res) => {
            this.violationRecord = res.data;

                console.log(this.violationRecord.length);
                this.month()
                this.roadFilter()

            })
    },
    roadFilter(){
        var ctr=0;
        for(ctr=0;ctr<this.violationRecord.length;ctr++){
            if(this.roadList.includes(this.violationRecord[ctr]['roadID'])==false){
                this.roadList.push(this.violationRecord[ctr]['roadID']);
                console.log("road",this.roadList);
            }

        }
        console.log("asd",this.roadList);
    },
    road(){
        console.log("testVal",this.selectedRoad)
        this.violationRecordMonth= [];  
        if(this.selectedRoad == "All"){
                this.violationRecordMonth = this.violationRecordMonth1
        }
        else {
            for(let ctr=0;ctr<this.violationRecordMonth1.length;ctr++){
                if(this.violationRecordMonth1[ctr]['roadID']==this.selectedRoad){
                    this.violationRecordMonth.push(this.violationRecordMonth1[ctr])
                }

            }
        }
    },
    resultQuery() {
      if (this.searchQuery) {
        return this.violationRecordMonth.filter(item => {
          return this.searchQuery
            .toLowerCase()
            .split(" ")
            .every(v => item.roadName.toLowerCase().includes(v));   
        });
      } else {
          this.violationNumber= this.violationRecordMonth.length
        return this.violationRecordMonth;
      }
    }  




}

}
</script>

<style scoped>
.headContainer{
    display: flex;
    justify-content: space-between;
    width: 100%;
    padding:0px 20px 0px 20px ;
}
.headContainer div{
    display:flex
}
.headContainer h5{
    padding-left:20px;
    margin:auto;
    font-family: 'Roboto';
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
.selection input{
    width:100%;
    outline: none;
    background-color:transparent;
    border:none;
    color:white;
    padding-left:10px;
}
.selection button{
    border:none;
    background-color:transparent;
}
.selection button img{
    margin:auto
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
.mainContainer{
    margin-top: 20px;
    border:2px solid #8F8F9C;
    border-radius: 20px;;
    min-height: 300px

}
table{
    width:100%;
    text-align: center;
     border-radius:20px;
     border-radius:100px;
}
table .headerColumn{
    border-bottom:2px solid #8F8F9C;
    font-family:'Roboto';
}
table tr{
    padding:10px;
}
table .headerColumn th{
    font-family:'Roboto';
    padding:20px;
    font-size:12px;
    font-style:normal   ;
}
table .containerValue td{
padding-top:20px;
font-size: 12px;
}
</style>