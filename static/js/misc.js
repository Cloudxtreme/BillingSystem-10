Math.roundP = function(num, precision){
   var pow = Math.pow(10, precision || 0);
   return (Math.round(num*pow) / pow);
};
