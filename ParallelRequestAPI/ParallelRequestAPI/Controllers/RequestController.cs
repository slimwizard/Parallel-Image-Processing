using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using ParallelRequestAPI.Helpers;

namespace ParallelRequestAPI.Controllers
{
    [Route("api/[controller]")]
    public class RequestController : Controller
    {

        [HttpGet]
        public string GetValues() {
            
            return "value";
        }

        // POST api/values
        [HttpPost]
        public string Post([FromForm] IFormFile file)
        {
            var path = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", file.FileName);
            using (var stream = new FileStream(path, FileMode.Create))
            {
                file.CopyToAsync(stream);
            }

            //string returnValue = "hi";
            return "hi";
        }


    }
}
