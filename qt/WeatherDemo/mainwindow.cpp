#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QProcess> // to call python script

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_updateValues_clicked()
{
    // Call python script here once
    QProcess p;
        QStringList params;

        params << "readValuesUpdateSheet.py -arg1 arg1";
        p.start("python", params);
        p.waitForFinished(-1);
        QString p_stdout = p.readAll();
        //ui->lineEdit->setText(p_stdout);
}

void MainWindow::on_radioButton_clicked()
{
    // Call python script every "updateValuesInterval"
}
