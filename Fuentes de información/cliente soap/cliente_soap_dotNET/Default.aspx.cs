using System;
using camara_diputado;

public partial class _Default : System.Web.UI.Page
{
    private camara_diputado.WSDiputadoSoapClient cd_SoapClient;

    protected void Page_Load(object sender, EventArgs e)
    {
        cd_SoapClient = new WSDiputadoSoapClient();

        ListarDiputados();
    }

    private void ListarDiputados()
    {
        camara_diputado.Diputado diputado;

        try
        {
            diputado = cd_SoapClient.retornarDiputado(208);

            Response.Write("Nombre:" + diputado.Nombre + "<br />");
            Response.Write("Paterno:" + diputado.ApellidoPaterno + "<br />");
        }
        catch (Exception ex)
        {
            Response.Write(ex.Message);
        }
    }
}