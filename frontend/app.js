const authSec = document.getElementById("auth-section");


async function deleteProduct(id) {
await api("DELETE", "/v1/products/" + id);
loadAdminProducts();
}


// ------------------------
// LOGOUT
// ------------------------
function logout() {
clearToken();
location.reload();
}


// -----------------------------------------
// INIT ON PAGE LOAD
// -----------------------------------------
(function init() {


const token = localStorage.getItem("token");


// No token → show login/register page
if (!token) {
showAuthPage();
return;
}


// Try decoding payload
let payload = null;
try {
payload = JSON.parse(atob(token.split(".")[1]));
} catch (e) {
// invalid token → clear & go to login
localStorage.removeItem("token");
showAuthPage();
return;
}


const roles = payload.roles || [];


// TOKEN VALID → decide dashboard
if (roles.includes("admin")) {
showAdminDashboard();
} else {
showUserDashboard();
}
})();


function showAuthPage() {
authSec.classList.remove("hidden");
adminSec.classList.add("hidden");
userSec.classList.add("hidden");
logoutBtn.classList.add("hidden");
}