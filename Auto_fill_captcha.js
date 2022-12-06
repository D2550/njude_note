// ==UserScript==
// @name         南大自动验证码
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  自动填充南大远程学习平台验证码
// @author       ccadmin
// @match        https://www.njude.com.cn/stuloginnew/LoginUInew.asp
// @icon         https://www.nju.edu.cn/_upload/tpl/01/36/310/template310/images/16.ico
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
     console.log(verifyCode.options.code);
     document.getElementById('code_img_input').value = verifyCode.options.code;
})();
