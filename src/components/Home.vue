<template>
<div class="header container-fluid">
    <div class="logoContainer">
        <div class="logo">
        <img alt="Vue logo" src="icons/Logo.svg">
        </div>
        <p class="logoLabel">DetectCore</p>
    </div>
</div>
<div class="logInContainer">
    <div class="loginForm text-white">
        <h4 class="text-white">Login</h4>
        <h6 class="text-muted pb-3 ">Parking is more than you think!</h6>
        <form @submit.prevent="onSubmit">
            <label>USERNAME</label>
            <input type="text" required/>
            <label >PASSWORD</label>
            <input type="password"/>
            <router-link to="/dashboard"><button type="submit">Login</button></router-link>
        </form>
    </div>
    <div class="rigthContainer">
        <div class="filter"></div>
        <div class="containerItems text-center text-white">
        <div class="rigthLogo">
            <img src="icons/logoWhite.svg"/>
        </div>
        <h1 class="text-white">DetectCore</h1>
        <p>A CCTV Software Application that can detect the vehicle’s
             violation (5 minutes rule) on the public road</p>
        </div>
    </div>
</div>
</template>

<script>

export default {
name: 'Home',
}
</script>
<style>

body{
background-color:#1D1F32
}
</style>
<style scoped>
.header{
    
    height: 55px;
    background: #272741;
box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
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
    font-family: 'Times New Roman', Times, serif;
    color:#678ADD;
    font-size: 18px;
    
}
.logInContainer{
    display: flex;
    margin: auto;
    justify-content: center;
    margin-top:55px;
    background: #272741;
    box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
    border-radius: 20px;
    font-family: 'Roboto', sans-serif;;
    width: max-content;
}
.loginForm{
    padding:50px ;
}
.loginForm form{
    display: flex;
    flex-direction: column;

}
input{
    width: 467px;
    height:33px;
    margin-bottom:10px;
    margin-top:5px;
    padding-left:10px;
    border-radius:5px;
    border:1px solid #C4C4C4;
    color:whitesmoke;
    font-family:'Roboto';
    background-color: transparent;
   outline: none;    
}
button{
    background-color: #678ADD;
    height: 49px;
    width: 467px;
    margin-top:30px;
    border:none;
    color:white;

}
label{
font-size:14px;
margin-bottom:5px;
}

.rigthContainer{
    position: relative;
    background-image: url('/image/image1.jpg');
    width:580px;
    height: 470px;
    border-top-right-radius:20px ;
    border-bottom-right-radius:20px ;
    background-color: #1D1F32;
    display: flex;
    justify-content: center;
}
.filter{

position: absolute;
background: rgba(39, 39, 65, 0.6);
border-radius: 0px 20px 20px 0px;
width:100%;
height: 100%;
}
.rigthLogo{
    display: flex;
    justify-content: center;
    width:min-content;
    border:3px solid white;
    z-index:0;
    width:87px;
    height: 87px;
    margin: auto;
}
.rigthLogo img{
    width: 59px;
    height: 62px;
    margin:auto;
}
.containerItems{
    margin: auto;
    z-index: 0;
    width: 415px;
}
.containerItems h1{
font-family: 'Times New Roman', Times, serif;
}
.containerItems p{
font-size: 14px;
}
</style>