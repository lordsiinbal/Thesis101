<template>
    <div class="container">
<div class="headContainer">
      <div class="text-white">
          <h5>{{roadNumber}}</h5>
          <h5> Road</h5>
      </div>
      <div>
                <div class='selection text-white'>
                    <input type="search" v-model="searchQuery" placeholder="Search"/>
                    <button><img src="icons/iconSearch.svg"/></button>
                </div>
        </div>

  </div>
  <div class="mainContainer">
      <table>
      <tr class="headerColumn text-white">
            <th> Road ID</th>
            <th> Road Name</th>
            <th> Screenshot</th>
      </tr>
      <tr class="containerValue container text-white" v-for="record in resultQuery()" :key="record.roadID" >
            <td> {{record.roadID}}</td>
            <td> {{record.roadName}}</td>
            <!-- <td> <img :src="record.screenShot"></td> -->
            
      </tr>
  </table>
  </div>
  
    </div>
  
</template>

<script>
import api from '../api';
export default {
data(){
    return{
        searchQuery: null,
        roadNumber:"",
        roadRecord1:[
            {   
                roadID:'',
                roadName:'',
                roadBoundaryCoordinates:'',
                roadCaptured:''
            },
        ]
    }
},
created(){
    this.getRoad();

},
methods:{

    getRoad(){
        api
            .get("/RoadFetchAll")
            .then((res) => {
            this.roadRecord1 = res.data;

                console.log(this.roadRecord1[0]);


            })
    },
     resultQuery() {
      if (this.searchQuery) {
        return this.roadRecord1.filter(item => {
          return this.searchQuery
            .toLowerCase()
            .split(" ")
            .every(v => item.roadName.toLowerCase().includes(v));   
        });
      } else {
          this.roadNumber= this.roadRecord1.length
        return this.roadRecord1;
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
.selection input{
    width:100%;
    outline: none;
    background-color:transparent;
    border:none;
    padding-left:10px;
    color:white;
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
    min-height: 300px;
    padding-bottom:20px;

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