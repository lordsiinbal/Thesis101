<template>
    <div class="container">
<div class="headContainer">
      <div class="text-white">
          <h5>100,000</h5>
          <h5> Violations</h5>
      </div>
      <div>
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
                <div class='selection text-white'>
                    <input type="seach" placeholder="search"/>
                    <button><img src="icons/iconSearch.svg"/></button>
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
      <tr class="containerValue container text-white" v-for="record in violationRecord" :key="record.violationNumber" >
            <td> {{record.violationNumber}}</td>
            <td> {{record.vehicleId}}</td>
            <td> {{record.roadName}}</td>
            <td> {{record.roadId}}</td>
            <td> {{record.lengthOfViolation}}</td>
            <td> {{record.startTime}}</td>
            <td> {{record.endTime}}</td>
      </tr>
  </table>
  </div>
  
    </div>
  
</template>

<script>
export default {
data(){
    return{
        violationRecord:[
            {   
                violationNumber:'V-0000001',
                vehicleId:'VE-0000001',
                roadName:'Cararayan #1',
                roadId:'R-0000001',
                lengthOfViolation:'10 minutes',
                startTime:'2/17/2022 5:05:00',
                endTime:'2/17/2022 5:15:00'
            },
            {   
                violationNumber:'V-0000002',
                vehicleId:'VE-0000001',
                roadName:'Cararayan #1',
                roadId:'R-0000001',
                lengthOfViolation:'10 minutes',
                startTime:'2/17/2022 5:05:00',
                endTime:'2/17/2022 5:15:00'
            }
        ]
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