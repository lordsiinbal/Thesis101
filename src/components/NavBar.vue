<template>
  <div class="header container-fluid">
    <div class="leftContainer">
        <div class="logoContainer">
        <div class="logo">
        <img alt="Vue logo" src="icons/Logo.svg">
        </div>
        <p class="logoLabel">DetectCore</p>
        </div>
        <router-link to="/dashboard" class="routeLink">
        <div class="menu">
        <div class="icon">
        <img alt="dashboardLogo" src="icons/iconCube.svg">
        </div>
        <p class="text-white">Dashboard</p>
        </div>
        </router-link>
        <router-link to="/table" class="routeLink">
        <div class="menu">
        <div class="icon">
        <img alt="dashboardLogo" src="icons/iconTable.svg">
        </div>
        <p class="text-white">Table</p>
        </div>
        </router-link>
    </div>
    <router-link to="/" class="routeLink">
    <div class="rightContainer">
        <button class="logoutBtn">
            <span>
            <img src="icons/iconLogout.svg"/>
            Logout</span>
            </button>
    </div>
    </router-link>
    
</div>
</template>

<script>
export default {

}
</script>

<style scoped>
.leftContainer{
    display: flex;
}
.header{
    display: flex;
    position:fixed;
    top:0;
    justify-content: space-between;
    height: 55px;
    background: #272741;
    box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
    padding-right: 0px;
}
.logoContainer{
    display: flex;
    justify-content: center;
    width: min-content;
    height: 100%;
}
.logo{
    display: flex;
    align-content: center;
    width:38px;
    height:38px;
    margin:auto;
    border: 2px solid #678ADD;
}
.logo img{
    width:26px;
    height:27px;
    margin:auto
    
}
.logoLabel{
    margin:auto;
    padding-left: 5px;
    padding-right: 15px;
    font-family: 'Times New Roman', Times, serif;
    color:#678ADD;
    font-size: 18px;
    
}

/**/
.menu{
    display: flex;
    margin: auto;
    margin-left: 10px;
    margin-right: 10px;
    cursor: pointer;
    height: 100%;
}
.menu div{
    display: flex;
    margin: auto;
}
.menu  p{
    margin:auto;
    padding-top:3px;
    padding-left: 5px;
    font-family: 'Roboto';
    font-size: 14px;
    text-decoration: none;   
}
.logoutBtn{
    display:flex;
    margin:auto;
    margin-top:auto;
    justify-content: center;
    justify-self: center;
    width:105px;
    height: 100%;
    background-color:#678ADD;
    color:white;
    border:none;
}
.logoutBtn span{
    display: flex;
margin: auto;
}

/*Logout container */
.rightContainer{
    display:flex;
    justify-content: center;
    height: 100%;
}
/* */
.routeLink{
    text-decoration: none;
}
.router-link-active{
  background-color:#1D1F32;
  display: flex;
  text-decoration: none;
}


</style>