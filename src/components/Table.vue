<template>
  <NavBar/>
  <div class=" headerContainer ">
    <div class="headerMenu" :class="{active:activeBtn=='Violation'}"  @click="change_component('Violation')">
      <span>
        <img src="icons/iconIllegalPark.svg"/>
        <h6 class="text-white">Violation</h6>
      </span>
    </div>
    <div @click="change_component('Road')" class="headerMenu" :class="{active:activeBtn=='Road'}">
      <span>
        <img src="icons/iconRoad.svg"/>
        <h6 class="text-white">Road</h6>
      </span>
    </div>
  </div>
  <div class="componentContainer container">
    <component :is="component"/>
  </div>
</template>

<script>
import NavBar from './NavBar.vue'
import Violation from './Violation.vue'
import Road from './Road.vue'
export default {
components:{
    NavBar,
    Violation,
    Road
},
data(){
  return{
    component:'Violation',
    activeBtn:'Violation'
  }
},
methods:{
    change_component(e){
          if(e=='Violation'){
            this.component='Violation'
            this.activeBtn='Violation'
          }
          else{
            this.component='Road'
            this.activeBtn='Road'
          }
      },

}

}
</script>

<style scode>
.active{

  border-bottom:4px solid #678ADD;
}
.headerContainer{
  display:flex;
  margin-top:3.5%;
  padding-top:20px;
  background-color:#1D1F32;
  border-bottom: 2px solid #678ADD;
  position: sticky;
  position: -webkit-sticky;
  top: 0;
}
.headerMenu{
  
  width:133px;
  font-family: 'Roboto';
}
.headerMenu span{
  display:flex;
  margin: auto;
  cursor:pointer;
  margin-bottom:5px;
  width:min-content;
}
.headerMenu span img{
  width:27.5px;
  height:27.5px;
  margin:auto;
}
.headerMenu span h6{
  margin:auto;
  padding:5px;
}
.componentContainer{
  display: flex;
  margin:auto;
  margin-top:5%;
  padding-bottom:20px;
}
</style>